package org.pusingcuk.studio;

import android.app.Activity;
import android.app.AlertDialog;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.content.Intent;
import android.net.Uri;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.ArrayAdapter;
import android.widget.Spinner;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONObject;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;
import java.security.KeyStore;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import java.util.regex.Matcher;
import java.util.Arrays;
import java.util.regex.Pattern;

public final class MainActivity extends Activity {
    private static final int MAX_SOURCE_BYTES = 64 * 1024, MAX_STDIN_BYTES = 16 * 1024;
    private static final int MAX_AI_CONTEXT_CHARS = 12000, MAX_AI_QUESTION_CHARS = 3000;
    private static final String AI_KEY_ALIAS = "org.pusingcuk.studio.gemini.key.v1";
    private static final String AI_PREFS = "pusingcuk_ai_secure";
    private static final String AI_KEY_PREF = "gemini_key_encrypted";
    private static final String[] TEMPLATE_LABELS = {"Halo dunia", "Kalkulasi belanja", "Rekap kas sederhana", "Input nama interaktif"};
    private static final String[] TEMPLATE_FILES = {"halo_dunia", "kalkulasi_belanja", "rekap_kas", "sapa_pengguna"};
    private static final String[] TEMPLATE_SOURCES = {
        "jancuk\nlah nama = \"Dunia\"\nhedeh \"Halo, \" + nama\nselesai jancuk\n",
        "jancuk\nlah harga = 15000\nlah jumlah = 3\nlah total = harga * jumlah\nhedeh \"Total belanja: \" + teks(total)\nselesai jancuk\n",
        "jancuk\nlah pendapatan = 2500000\nlah pengeluaran = 1200000\nlah sisa = pendapatan - pengeluaran\nhedeh \"Sisa: \" + teks(sisa)\nnjir sisa >= 0\n    hedeh \"Status: aman\"\nkampret\n    hedeh \"Status: defisit\"\nselesai njir\nselesai jancuk\n",
        "jancuk\ntanya nama = \"Nama kamu: \"\nhedeh \"Halo, \" + nama\nselesai jancuk\n"
    };
    private static final String[] AI_MODEL_LABELS = {"Gemini 3.5 Flash-Lite · hemat", "Gemini 3.8 Flash · lebih kuat"};
    private static final String[] AI_MODEL_IDS = {"gemini-3.5-flash-lite", "gemini-3.8-flash"};
    private static final String AI_SYSTEM_INSTRUCTION = "Kamu membantu di PusingCuk Studio. Bantu pengguna pemula dengan bahasa Indonesia yang jelas dan tidak merendahkan. Bahasa target adalah .cuk versi 0.6-dev; jangan mengarang keyword, built-in, atau kemampuan runtime. Program biasanya dimulai dengan jancuk dan diakhiri selesai jancuk. Gunakan hanya sintaks .cuk yang dikenal, jangan mengasumsikan Python/JavaScript bisa langsung dipakai sebagai sintaks .cuk. Runtime aplikasi Android saat ini adalah subset native C: jelaskan bila fitur mungkin belum didukung. Jangan mengklaim source telah dikompilasi atau diuji jika belum ada bukti. Jangan meminta atau menampilkan secret dan jangan membuat kode untuk mengakses token atau menjalankan shell. Jika pengguna meminta program atau perbaikan source, sertakan satu blok kode berlabel cuk yang berisi program lengkap; selain itu jelaskan sesuai kebutuhan. Jawaban adalah saran AI eksternal, bukan hasil eksekusi ToolRegistry PusingCuk AI.";
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private EditText source, stdin;
    private TextView output, status;
    private Button runButton, aiButton, applyAiButton;
    private String pendingAiCode;
    private File runtime, compiledDemo, projectDir, projectFile;
    private TextView projectLabel;

    private int dp(float n) { return (int)(n * getResources().getDisplayMetrics().density + 0.5f); }
    private TextView label(String text, int size, int color) {
        TextView v = new TextView(this); v.setText(text); v.setTextSize(size); v.setTextColor(color);
        v.setPadding(dp(2), dp(8), dp(2), dp(6)); return v;
    }
    private LinearLayout column() {
        LinearLayout v = new LinearLayout(this); v.setOrientation(LinearLayout.VERTICAL);
        v.setPadding(dp(14), dp(8), dp(14), dp(10)); return v;
    }
    private Button button(String text, LinearLayout parent, View.OnClickListener click) {
        Button b = new Button(this); b.setText(text); b.setOnClickListener(click);
        parent.addView(b, new LinearLayout.LayoutParams(-1, -2)); return b;
    }
    private EditText editor(String hint, int lines) {
        EditText e = new EditText(this); e.setTextColor(Color.rgb(225,237,249));
        e.setHintTextColor(Color.rgb(132,151,176)); e.setHint(hint); e.setTextSize(14);
        e.setTypeface(Typeface.MONOSPACE); e.setGravity(Gravity.TOP|Gravity.START);
        e.setPadding(dp(12),dp(12),dp(12),dp(12)); e.setBackgroundColor(Color.rgb(9,15,28));
        e.setMinLines(lines); e.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_MULTI_LINE|InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
        e.setHorizontallyScrolling(true); return e;
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        cleanupStaleRunFiles();
        getWindow().setStatusBarColor(Color.rgb(10,15,28)); getWindow().setNavigationBarColor(Color.rgb(10,15,28));
        projectDir = new File(getFilesDir(), "projects");
        if (!projectDir.exists()) projectDir.mkdirs();
        projectFile = new File(projectDir, "program.cuk"); buildUi(); installRuntime(); loadProject();
    }

    // Cache files are app-private, but a force-stop can leave source files behind.
    // Remove only old files created by this runner; never clear the whole cache.
    private void cleanupStaleRunFiles() {
        File work = new File(getCacheDir(), "run");
        File[] files = work.listFiles((dir, name) ->
                name.startsWith("program-") && (name.endsWith(".cuk") || name.endsWith(".pusingcuk")));
        if (files == null) return;
        long cutoff = System.currentTimeMillis() - TimeUnit.HOURS.toMillis(24);
        for (File file : files) {
            if (file.isFile() && file.lastModified() < cutoff) file.delete();
        }
    }

    private void buildUi() {
        ScrollView scroll = new ScrollView(this); scroll.setFillViewport(true); scroll.setBackgroundColor(Color.rgb(10,16,32));
        LinearLayout page = column(); scroll.addView(page); setContentView(scroll);
        TextView title = label("Pusingcuk Studio",23,Color.rgb(98,214,181)); title.setTypeface(Typeface.DEFAULT,Typeface.BOLD); page.addView(title);
        page.addView(label("Editor + runtime native · Android",13,Color.LTGRAY));
        LinearLayout actions = column(); actions.setPadding(0,dp(2),0,dp(2)); page.addView(actions);
        runButton = button("▶ Jalankan",actions,v->runProgram());
        button("Jalankan demo .cuk hasil kompilasi native",actions,v->runCompiledDemo());
        button("Proyek baru", actions, v -> showNewProjectDialog());
        button("Simpan proyek",actions,v->saveProject());
        button("Buka proyek lokal",actions,v->showProjectPicker());
        button("Impor file publik dari GitHub",actions,v->showGitHubImport());
        button("Bagikan / ekspor kode",actions,v->shareProject());
        aiButton = button("Bantuan PusingCuk AI · online (opsional)", actions, v -> showAiAssistant());
        button("Buat / kelola API key Gemini", actions, v -> startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://aistudio.google.com/app/apikey"))));
        applyAiButton = button("Terapkan kode hasil AI ke editor", actions, v -> applyAiCode());
        applyAiButton.setVisibility(View.GONE);
        projectLabel = label(projectFile == null ? "program.cuk" : projectFile.getName(),16,Color.WHITE);
        page.addView(projectLabel);
        source = editor("Tulis kode Pusingcuk di sini…",14); page.addView(source,new LinearLayout.LayoutParams(-1,dp(310)));
        page.addView(label("Input program (stdin) — satu baris per jawaban",14,Color.WHITE));
        stdin = editor("Contoh: Budi",2); page.addView(stdin,new LinearLayout.LayoutParams(-1,dp(80)));
        page.addView(label("Terminal keluaran",16,Color.WHITE));
        status = label("Menyiapkan runtime native…",12,Color.rgb(98,214,181)); page.addView(status);
        output = label("Contoh kode akan dimuat setelah runtime disiapkan.",13,Color.rgb(214,247,233));
        output.setTypeface(Typeface.MONOSPACE); output.setBackgroundColor(Color.rgb(5,11,22));
        output.setPadding(dp(12),dp(12),dp(12),dp(12)); page.addView(output,new LinearLayout.LayoutParams(-1,-2));
        page.addView(label("Fitur mengikuti matriks runtime native. Eksekusi bukan sandbox; jangan jalankan kode tak tepercaya.",12,Color.LTGRAY));
    }

    private void installRuntime() {
        String abi = null;
        for (String s : Build.SUPPORTED_ABIS) if ("arm64-v8a".equals(s)||"armeabi-v7a".equals(s)) { abi=s; break; }
        if (abi == null) { status.setText("Perangkat tidak memakai ABI ARM yang didukung."); runButton.setEnabled(false); return; }
        try (InputStream in = getAssets().open("bin/"+abi+"/pusingcuk-native")) {
            runtime = new File(getFilesDir(),"pusingcuk-native");
            try (OutputStream out = new FileOutputStream(runtime)) { byte[] b=new byte[8192]; int n; while((n=in.read(b))!=-1) out.write(b,0,n); }
            if (!runtime.setExecutable(true,true)) throw new IllegalStateException("Tidak dapat mengaktifkan runtime.");
            try (InputStream demoIn = getAssets().open("bin/"+abi+"/pusingcuk-compiled-demo")) {
                compiledDemo = new File(getFilesDir(),"pusingcuk-compiled-demo");
                try (OutputStream demoOut = new FileOutputStream(compiledDemo)) {
                    byte[] chunk = new byte[8192]; int count;
                    while ((count = demoIn.read(chunk)) != -1) demoOut.write(chunk,0,count);
                }
                if (!compiledDemo.setExecutable(true,true)) throw new IllegalStateException("Demo hasil kompilasi tidak dapat dijalankan.");
            }
            status.setText("Runtime native siap · "+abi+" · compiler C tersedia");
            source.setText("jancuk\nlah nama = \"Dunia\"\n\nfungsi tambah(a, b)\n    balek a + b\nselesai fungsi\n\nhedeh \"Halo, \" + nama\nhedeh tambah(20, 22)\nselesai jancuk");
        } catch(Exception e) { status.setText("Runtime gagal disiapkan: "+e.getMessage()); runButton.setEnabled(false); }
    }


    private void saveProject() {
        try {
            if (projectDir == null || !projectDir.isDirectory() || projectFile == null || !projectFile.getParentFile().equals(projectDir))
                throw new IllegalStateException("Lokasi proyek tidak valid.");
            String code = source.getText().toString();
            if (utf8Length(code) > MAX_SOURCE_BYTES) throw new IllegalArgumentException("Kode melebihi 64 KiB.");
            try (FileOutputStream out = new FileOutputStream(projectFile)) { out.write(code.getBytes(StandardCharsets.UTF_8)); }
            projectLabel.setText(projectFile.getName());
            status.setText("Tersimpan: " + projectFile.getName());
            Toast.makeText(this, "Tersimpan: " + projectFile.getName(), Toast.LENGTH_SHORT).show();
        } catch (Exception e) { toastError("Gagal menyimpan: " + e.getMessage()); }
    }

    private void loadProject() {
        try {
            if (projectFile == null || !projectFile.isFile()) {
                if (source != null && source.length() == 0) source.setText("jancuk\nhedeh \"Halo, dunia!\"\nselesai jancuk");
                if (projectLabel != null && projectFile != null) projectLabel.setText(projectFile.getName());
                return;
            }
            if (!projectFile.getParentFile().equals(projectDir) || projectFile.length() > MAX_SOURCE_BYTES)
                throw new IllegalStateException("Lokasi atau ukuran file proyek tidak valid (maksimum 64 KiB).");
            try (FileInputStream in = new FileInputStream(projectFile); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
                byte[] b = new byte[4096]; int n;
                while ((n = in.read(b)) != -1) {
                    if (out.size() + n > MAX_SOURCE_BYTES) throw new IllegalStateException("File proyek lebih besar dari 64 KiB.");
                    out.write(b, 0, n);
                }
                source.setText(new String(out.toByteArray(), StandardCharsets.UTF_8));
            }
            projectLabel.setText(projectFile.getName());
            status.setText("Proyek dibuka: " + projectFile.getName());
        } catch (Exception e) { toastError("Gagal membuka: " + e.getMessage()); }
    }

    private void showProjectPicker() {
        File[] files = projectDir == null ? null : projectDir.listFiles((dir, name) ->
                name.endsWith(".cuk") || name.endsWith(".pusingcuk"));
        if (files == null || files.length == 0) {
            toastError("Belum ada file proyek. Tekan Proyek baru untuk mulai.");
            return;
        }
        Arrays.sort(files, (a, b) -> a.getName().compareToIgnoreCase(b.getName()));
        String[] names = new String[files.length];
        for (int i = 0; i < files.length; i++) names[i] = files[i].getName();
        new AlertDialog.Builder(this).setTitle("Buka proyek lokal")
                .setItems(names, (dialog, which) -> { projectFile = files[which]; loadProject(); })
                .setNegativeButton("Batal", null).show();
    }

    private void showNewProjectDialog() {
        new AlertDialog.Builder(this).setTitle("Pilih template .cuk")
                .setItems(TEMPLATE_LABELS, (dialog, which) -> promptNewProjectName(which))
                .setNegativeButton("Batal", null).show();
    }

    private void promptNewProjectName(int templateIndex) {
        EditText name = editor("Nama file tanpa ekstensi", 1);
        name.setSingleLine(true);
        name.setText(TEMPLATE_FILES[templateIndex]);
        new AlertDialog.Builder(this).setTitle("Nama proyek baru")
                .setView(name).setNegativeButton("Batal", null)
                .setPositiveButton("Buat", (dialog, which) -> {
                    String stem = name.getText().toString().trim();
                    if (stem.toLowerCase(java.util.Locale.ROOT).endsWith(".cuk"))
                        stem = stem.substring(0, stem.length() - 4);
                    if (!stem.matches("[A-Za-z0-9_-]{1,48}") || stem.contains("..")) {
                        toastError("Nama file gunakan huruf, angka, garis bawah, atau tanda hubung (maks. 48 karakter).");
                        return;
                    }
                    File next = new File(projectDir, stem + ".cuk");
                    if (next.exists()) {
                        toastError("Nama itu sudah ada. Buka proyek yang ada atau pilih nama lain.");
                        return;
                    }
                    projectFile = next;
                    source.setText(TEMPLATE_SOURCES[templateIndex]);
                    stdin.setText("");
                    pendingAiCode = null;
                    applyAiButton.setVisibility(View.GONE);
                    projectLabel.setText(projectFile.getName());
                    saveProject();
                }).show();
    }

    private void runProgram() {
        final String code=source.getText().toString(), input=stdin.getText().toString();
        if(runtime==null||!runtime.canExecute()){toastError("Runtime native belum siap.");return;}
        if(code.trim().isEmpty()){toastError("Kode tidak boleh kosong.");return;}
        if(utf8Length(code)>MAX_SOURCE_BYTES){toastError("Kode maksimum 64 KiB.");return;}
        if(utf8Length(input)>MAX_STDIN_BYTES){toastError("Input maksimum 16 KiB.");return;}
        runButton.setEnabled(false); status.setText("Program sedang berjalan…"); output.setText("");
        worker.execute(()->{
            File program=null; Process proc=null; BoundedOutputStream stdout=new BoundedOutputStream(), stderr=new BoundedOutputStream();
            try {
                File work=new File(getCacheDir(),"run"); if(!work.exists()&&!work.mkdirs())throw new IllegalStateException("Folder sementara gagal dibuat.");
                program=File.createTempFile("program-",".cuk",work);
                try(FileOutputStream out=new FileOutputStream(program)){out.write(code.getBytes(StandardCharsets.UTF_8));}
                proc=new ProcessBuilder(runtime.getAbsolutePath(),program.getAbsolutePath()).directory(work).start();
                final Process active=proc;
                Thread outReader=new Thread(()->copy(active.getInputStream(),stdout)); Thread errReader=new Thread(()->copy(active.getErrorStream(),stderr));
                outReader.start(); errReader.start();
                try(OutputStream in=proc.getOutputStream()){in.write(input.getBytes(StandardCharsets.UTF_8));in.flush();}
                boolean finished=proc.waitFor(3,TimeUnit.SECONDS);
                if(!finished){proc.destroyForcibly();proc.waitFor(500,TimeUnit.MILLISECONDS);}
                outReader.join(500);errReader.join(500);
                final boolean timeout=!finished; final int exit=finished?proc.exitValue():-1;
                final String outText=stdout.text(),errText=stderr.text();
                runOnUiThread(()->{
                    String text=outText;if(!errText.isEmpty())text+=(text.isEmpty()?"":"\n")+"[stderr]\n"+errText;
                    if(timeout){text+=(text.isEmpty()?"":"\n")+"Eksekusi dihentikan setelah 3 detik.";status.setText("Timeout");}
                    else status.setText(exit==0?"Selesai · exit 0":"Gagal · exit "+exit);
                    output.setText(text.isEmpty()?"(program selesai tanpa keluaran)":text);runButton.setEnabled(true);
                });
            } catch(Exception e){String m=e.getMessage()==null?e.getClass().getSimpleName():e.getMessage();runOnUiThread(()->{status.setText("Eksekusi gagal");output.setText(m);runButton.setEnabled(true);});}
            finally{if(proc!=null&&proc.isAlive())proc.destroyForcibly();if(program!=null)program.delete();}
        });
    }


    // Generated from examples/android_native_demo.cuk by the Android NDK build.
    private void runCompiledDemo() {
        if (compiledDemo == null || !compiledDemo.canExecute()) {
            toastError("Demo hasil kompilasi .cuk belum tersedia di APK ini."); return;
        }
        runButton.setEnabled(false); status.setText("Menjalankan program .cuk hasil kompilasi native…"); output.setText("");
        worker.execute(() -> {
            Process proc = null;
            BoundedOutputStream stdout = new BoundedOutputStream(), stderr = new BoundedOutputStream();
            try {
                proc = new ProcessBuilder(compiledDemo.getAbsolutePath()).directory(getFilesDir()).start();
                final Process active = proc;
                Thread outReader = new Thread(() -> copy(active.getInputStream(), stdout));
                Thread errReader = new Thread(() -> copy(active.getErrorStream(), stderr));
                outReader.start(); errReader.start();
                boolean finished = proc.waitFor(3, TimeUnit.SECONDS);
                if (!finished) { proc.destroyForcibly(); proc.waitFor(500, TimeUnit.MILLISECONDS); }
                outReader.join(500); errReader.join(500);
                final boolean timeout = !finished; final int exit = finished ? proc.exitValue() : -1;
                final String outText = stdout.text(), errText = stderr.text();
                runOnUiThread(() -> {
                    String text = outText;
                    if (!errText.isEmpty()) text += (text.isEmpty() ? "" : "\n") + "[stderr]\n" + errText;
                    if (timeout) { text += (text.isEmpty() ? "" : "\n") + "Eksekusi dihentikan setelah 3 detik."; status.setText("Timeout"); }
                    else status.setText(exit == 0 ? "Kompilasi native berhasil · exit 0" : "Program hasil kompilasi gagal · exit " + exit);
                    output.setText(text.isEmpty() ? "(program selesai tanpa keluaran)" : text);
                    runButton.setEnabled(true);
                });
            } catch (Exception e) {
                String message = e.getMessage() == null ? e.getClass().getSimpleName() : e.getMessage();
                runOnUiThread(() -> { status.setText("Demo native gagal"); output.setText(message); runButton.setEnabled(true); });
            } finally { if (proc != null && proc.isAlive()) proc.destroyForcibly(); }
        });
    }

    private void showGitHubImport() {
        LinearLayout form=column();form.setPadding(dp(18),0,dp(18),0);
        EditText owner=editor("Pemilik repo",1);owner.setText("rllibo833-sudo");
        EditText repo=editor("Nama repo",1);repo.setText("pusingcuk");
        EditText path=editor("Path file .cuk",1);path.setText("examples/android_native_demo.cuk");
        form.addView(owner);form.addView(repo);form.addView(path);
        new AlertDialog.Builder(this).setTitle("Impor file publik GitHub")
          .setMessage("Versi awal membaca repo publik saja; belum mengirim commit ke GitHub.")
          .setView(form).setNegativeButton("Batal",null).setPositiveButton("Impor",(d,w)->{
            String o=owner.getText().toString().trim(),r=repo.getText().toString().trim(),p=path.getText().toString().trim();
            if(!o.matches("[A-Za-z0-9_.-]{1,100}")||!r.matches("[A-Za-z0-9_.-]{1,100}")||p.isEmpty()||p.startsWith("/")||p.contains("..")||p.contains("\\")){toastError("Nama repo atau path tidak valid.");return;}
            status.setText("Mengambil file GitHub publik…");
            worker.execute(()->{
                try{
                    String url="https://api.github.com/repos/"+o+"/"+r+"/contents/"+encodePath(p);
                    HttpURLConnection c=(HttpURLConnection)new URL(url).openConnection();c.setRequestMethod("GET");c.setConnectTimeout(8000);c.setReadTimeout(10000);
                    c.setRequestProperty("Accept","application/vnd.github+json");c.setRequestProperty("User-Agent","Pusingcuk-Studio-Android");
                    int code=c.getResponseCode();InputStream stream=code>=200&&code<300?c.getInputStream():c.getErrorStream();
                    String body=readText(stream,1024*1024);c.disconnect();
                    if(code<200||code>=300)throw new IllegalStateException("GitHub HTTP "+code+": "+body);
                    JSONObject json=new JSONObject(body);if(!"file".equals(json.optString("type")))throw new IllegalStateException("Path harus menunjuk satu file.");
                    String encoded=json.optString("content","").replaceAll("\\s","");if(encoded.isEmpty())throw new IllegalStateException("Isi kosong atau terlalu besar untuk API Contents.");
                    byte[] bytes=android.util.Base64.decode(encoded,android.util.Base64.DEFAULT);if(bytes.length>MAX_SOURCE_BYTES)throw new IllegalStateException("File melebihi 64 KiB.");
                    String text=new String(bytes,StandardCharsets.UTF_8);
                    runOnUiThread(()->{source.setText(text);saveProject();status.setText("Impor GitHub berhasil: "+p);});
                }catch(Exception e){String m=e.getMessage()==null?"Impor gagal":e.getMessage();runOnUiThread(()->{status.setText("Impor GitHub gagal");output.setText(m);});}
            });
          }).show();
    }

    // Optional online AI. Keys are encrypted by Android Keystore; editor source is opt-in.
    private void showAiAssistant() {
        LinearLayout form = column();
        form.setPadding(dp(18), 0, dp(18), 0);
        form.addView(label("Model AI", 14, Color.WHITE));
        Spinner model = new Spinner(this);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, AI_MODEL_LABELS);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        model.setAdapter(adapter);
        form.addView(model);
        form.addView(label("API key Google AI Studio", 14, Color.WHITE));
        EditText key = editor("Kunci tersimpan terenkripsi; kosongkan untuk memakai yang tersimpan", 1);
        key.setSingleLine(true);
        key.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD | InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
        form.addView(key, new LinearLayout.LayoutParams(-1, dp(54)));
        form.addView(label("Apa yang ingin kamu buat atau perbaiki?", 14, Color.WHITE));
        EditText question = editor("Contoh: buat program .cuk untuk menghitung belanja dan kembalian.", 4);
        question.setHorizontallyScrolling(false);
        form.addView(question, new LinearLayout.LayoutParams(-1, dp(112)));
        CheckBox includeCode = new CheckBox(this);
        includeCode.setText("Kirim kode yang sedang ada di editor sebagai konteks");
        includeCode.setTextColor(Color.WHITE);
        includeCode.setTextSize(13);
        includeCode.setChecked(false);
        form.addView(includeCode);
        form.addView(label("Privasi: permintaan dikirim ke Google Gemini lewat HTTPS. Kode editor tidak dikirim kecuali kotak dicentang. API key disimpan terenkripsi di perangkat. Kuota/biaya mengikuti akun provider. Kode hasil AI tidak otomatis dijalankan.", 12, Color.LTGRAY));

        new AlertDialog.Builder(this)
            .setTitle("Bantuan PusingCuk AI")
            .setView(form)
            .setNegativeButton("Batal", null)
            .setNeutralButton("Hapus kunci", (dialog, which) -> deleteAiKey())
            .setPositiveButton("Tanya AI", (dialog, which) -> {
                String userQuestion = question.getText().toString().trim();
                String enteredKey = key.getText().toString().trim();
                if (userQuestion.isEmpty() || userQuestion.length() > MAX_AI_QUESTION_CHARS) {
                    toastError("Isi pertanyaan AI (maksimum 3.000 karakter).");
                    return;
                }
                if (enteredKey.length() > 512) {
                    toastError("API key terlalu panjang.");
                    return;
                }
                String context = "";
                if (includeCode.isChecked()) {
                    context = source.getText().toString();
                    if (context.length() > MAX_AI_CONTEXT_CHARS) {
                        toastError("Kode terlalu panjang untuk dikirim ke AI (maksimum 12.000 karakter).");
                        return;
                    }
                }
                final String prompt = buildAiPrompt(userQuestion, context);
                final String requestedModel = AI_MODEL_IDS[Math.max(0, Math.min(model.getSelectedItemPosition(), AI_MODEL_IDS.length - 1))];
                try {
                    if (!enteredKey.isEmpty()) saveAiKey(enteredKey);
                    String storedKey = readAiKey();
                    if (storedKey.isEmpty()) {
                        toastError("Masukkan API key Google AI Studio, atau batalkan untuk membuatnya.");
                        return;
                    }
                    aiButton.setEnabled(false);
                    applyAiButton.setVisibility(View.GONE);
                    pendingAiCode = null;
                    status.setText("Meminta bantuan AI online…");
                    output.setText("Menghubungi provider AI. Kode tidak dijalankan otomatis.");
                    worker.execute(() -> {
                        try {
                            String answer = requestGemini(storedKey, requestedModel, prompt);
                            String candidate = extractCukCode(answer);
                            runOnUiThread(() -> {
                                pendingAiCode = candidate;
                                applyAiButton.setVisibility(candidate == null ? View.GONE : View.VISIBLE);
                                status.setText(candidate == null ? "Jawaban AI diterima · belum ada blok kode .cuk" : "Jawaban AI diterima · source belum diverifikasi");
                                output.setText(answer);
                                aiButton.setEnabled(true);
                            });
                        } catch (Exception e) {
                            String message = e.getMessage() == null ? "Permintaan AI gagal." : e.getMessage();
                            runOnUiThread(() -> {
                                status.setText("Bantuan AI gagal");
                                output.setText(message + "\nPeriksa internet, API key, kuota, dan nama model. Kode tidak dijalankan.");
                                aiButton.setEnabled(true);
                            });
                        }
                    });
                } catch (Exception e) {
                    toastError("Kunci AI tidak dapat disimpan/dibaca. Coba hapus kunci lalu masukkan kembali.");
                }
            })
            .show();
    }

    private String buildAiPrompt(String question, String currentSource) {
        StringBuilder prompt = new StringBuilder();
        prompt.append("Permintaan pengguna:\n").append(question);
        if (!currentSource.isEmpty()) {
            prompt.append("\n\nSource .cuk yang secara eksplisit diizinkan pengguna untuk dikirim:\n[SOURCE .cuk]\n")
                  .append(currentSource).append("\n[AKHIR SOURCE .cuk]");
        }
        prompt.append("\n\nAturan: bantu pengguna memahami dan membuat program .cuk yang cocok dengan runtime Android yang terbatas. Jika memperbaiki kode, jelaskan singkat dan sertakan program lengkap dalam satu blok kode berlabel cuk. Jangan menyatakan berhasil dijalankan atau lintas-runtime sebelum ada hasil tes.");
        return prompt.toString();
    }

    private SecretKey getOrCreateAiEncryptionKey() throws Exception {
        KeyStore store = KeyStore.getInstance("AndroidKeyStore");
        store.load(null);
        if (store.containsAlias(AI_KEY_ALIAS)) return (SecretKey) store.getKey(AI_KEY_ALIAS, null);
        KeyGenerator generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(
                AI_KEY_ALIAS, KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setRandomizedEncryptionRequired(true)
                .build());
        return generator.generateKey();
    }

    private void saveAiKey(String value) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateAiEncryptionKey());
        byte[] encrypted = cipher.doFinal(value.getBytes(StandardCharsets.UTF_8));
        String packed = android.util.Base64.encodeToString(cipher.getIV(), android.util.Base64.NO_WRAP)
                + ":" + android.util.Base64.encodeToString(encrypted, android.util.Base64.NO_WRAP);
        getSharedPreferences(AI_PREFS, MODE_PRIVATE).edit().putString(AI_KEY_PREF, packed).apply();
    }

    private String readAiKey() throws Exception {
        String packed = getSharedPreferences(AI_PREFS, MODE_PRIVATE).getString(AI_KEY_PREF, "");
        if (packed.isEmpty()) return "";
        String[] pieces = packed.split(":", 2);
        if (pieces.length != 2) throw new IllegalStateException("Penyimpanan kunci tidak valid.");
        byte[] iv = android.util.Base64.decode(pieces[0], android.util.Base64.NO_WRAP);
        byte[] encrypted = android.util.Base64.decode(pieces[1], android.util.Base64.NO_WRAP);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, getOrCreateAiEncryptionKey(), new GCMParameterSpec(128, iv));
        return new String(cipher.doFinal(encrypted), StandardCharsets.UTF_8);
    }

    private void deleteAiKey() {
        try {
            getSharedPreferences(AI_PREFS, MODE_PRIVATE).edit().remove(AI_KEY_PREF).apply();
            KeyStore store = KeyStore.getInstance("AndroidKeyStore");
            store.load(null);
            if (store.containsAlias(AI_KEY_ALIAS)) store.deleteEntry(AI_KEY_ALIAS);
            Toast.makeText(this, "API key AI lokal dihapus", Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            toastError("Gagal menghapus kunci AI.");
        }
    }

    private String requestGemini(String apiKey, String modelId, String prompt) throws Exception {
        if (!"gemini-3.5-flash-lite".equals(modelId) && !"gemini-3.8-flash".equals(modelId))
            throw new IllegalArgumentException("Model AI tidak diizinkan.");
        URL url = new URL("https://generativelanguage.googleapis.com/v1beta/models/" + modelId + ":generateContent");
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setConnectTimeout(15000);
        connection.setReadTimeout(45000);
        connection.setInstanceFollowRedirects(false);
        connection.setDoOutput(true);
        connection.setRequestProperty("Accept", "application/json");
        connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
        connection.setRequestProperty("x-goog-api-key", apiKey);
        JSONObject system = new JSONObject().put("parts",
                new org.json.JSONArray().put(new JSONObject().put("text", AI_SYSTEM_INSTRUCTION)));
        JSONObject user = new JSONObject().put("role", "user").put("parts",
                new org.json.JSONArray().put(new JSONObject().put("text", prompt)));
        JSONObject payload = new JSONObject()
                .put("system_instruction", system)
                .put("contents", new org.json.JSONArray().put(user))
                .put("generationConfig", new JSONObject().put("temperature", 0.2).put("maxOutputTokens", 3072));
        try {
            byte[] body = payload.toString().getBytes(StandardCharsets.UTF_8);
            try (OutputStream stream = connection.getOutputStream()) { stream.write(body); }
            int code = connection.getResponseCode();
            InputStream responseStream = (code >= 200 && code < 300) ? connection.getInputStream() : connection.getErrorStream();
            String responseBody = readText(responseStream, 256 * 1024);
            if (code < 200 || code >= 300) {
                String detail = "provider menolak permintaan";
                try {
                    JSONObject error = new JSONObject(responseBody).optJSONObject("error");
                    if (error != null && !error.optString("message", "").isEmpty()) detail = error.optString("message");
                } catch (Exception ignored) { }
                if (detail.length() > 500) detail = detail.substring(0, 500);
                throw new IOException("Gemini HTTP " + code + ": " + detail);
            }
            JSONObject response = new JSONObject(responseBody);
            org.json.JSONArray candidates = response.optJSONArray("candidates");
            StringBuilder answer = new StringBuilder();
            if (candidates != null) {
                for (int i = 0; i < candidates.length(); i++) {
                    JSONObject candidate = candidates.optJSONObject(i);
                    JSONObject content = candidate == null ? null : candidate.optJSONObject("content");
                    org.json.JSONArray parts = content == null ? null : content.optJSONArray("parts");
                    if (parts == null) continue;
                    for (int j = 0; j < parts.length(); j++) {
                        JSONObject part = parts.optJSONObject(j);
                        if (part != null && part.has("text")) {
                            if (answer.length() > 0) answer.append("\n");
                            answer.append(part.optString("text"));
                        }
                    }
                    if (answer.length() > 0) break;
                }
            }
            if (answer.length() == 0) throw new IOException("Model tidak menghasilkan jawaban teks (mungkin diblokir oleh kebijakan provider).");
            return answer.toString();
        } finally {
            connection.disconnect();
        }
    }

    private String extractCukCode(String answer) {
        Matcher matcher = Pattern.compile("\\x60{3}(?:cuk|pusingcuk)\\s*\\r?\\n([\\s\\S]*?)\\x60{3}", Pattern.CASE_INSENSITIVE).matcher(answer);
        if (!matcher.find()) return null;
        String code = matcher.group(1).trim();
        if (code.isEmpty() || utf8Length(code) > MAX_SOURCE_BYTES) return null;
        return code + "\n";
    }

    private void applyAiCode() {
        if (pendingAiCode == null || pendingAiCode.trim().isEmpty()) {
            toastError("Belum ada source .cuk dari jawaban AI.");
            return;
        }
        source.setText(pendingAiCode);
        pendingAiCode = null;
        applyAiButton.setVisibility(View.GONE);
        status.setText("Kode AI disalin ke editor · belum diverifikasi");
        Toast.makeText(this, "Kode masuk editor. Periksa dulu sebelum menjalankan.", Toast.LENGTH_LONG).show();
    }


    private String encodePath(String path)throws Exception {
        StringBuilder b=new StringBuilder();for(String part:path.split("/")){if(b.length()>0)b.append('/');b.append(java.net.URLEncoder.encode(part,"UTF-8").replace("+","%20"));}return b.toString();
    }
    private String readText(InputStream in,int max)throws Exception {
        if(in==null)return "";try(InputStream input=in;ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] b=new byte[4096];int total=0,n;while((n=input.read(b))!=-1){total+=n;if(total>max)throw new IllegalStateException("Respons GitHub terlalu besar.");out.write(b,0,n);}return out.toString("UTF-8");
        }
    }
    private void shareProject() {
        String code=source.getText().toString();if(utf8Length(code)>MAX_SOURCE_BYTES){toastError("Kode maksimum 64 KiB.");return;}
        Intent intent=new Intent(Intent.ACTION_SEND);intent.setType("text/plain");intent.putExtra(Intent.EXTRA_SUBJECT,projectFile == null ? "program.cuk" : projectFile.getName());intent.putExtra(Intent.EXTRA_TEXT,code);
        startActivity(Intent.createChooser(intent,"Bagikan kode Pusingcuk"));
    }
    private static int utf8Length(String s){return s.getBytes(StandardCharsets.UTF_8).length;}
    private static final class BoundedOutputStream extends OutputStream {
        private static final int MAX_CAPTURE_BYTES = 256 * 1024;
        private final ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        private boolean truncated;

        @Override public synchronized void write(int value) {
            if (buffer.size() < MAX_CAPTURE_BYTES) buffer.write(value);
            else truncated = true;
        }

        @Override public synchronized void write(byte[] bytes, int offset, int length) {
            if (length <= 0) return;
            int remaining = MAX_CAPTURE_BYTES - buffer.size();
            if (remaining > 0) buffer.write(bytes, offset, Math.min(remaining, length));
            if (length > remaining) truncated = true;
        }

        synchronized String text() {
            String result = new String(buffer.toByteArray(), StandardCharsets.UTF_8);
            return truncated ? result + "\n[output dipotong: batas 256 KiB per stream]" : result;
        }
    }

    private static void copy(InputStream in,BoundedOutputStream out){
        try(InputStream input=in){byte[] b=new byte[4096];int n;while((n=input.read(b))!=-1)out.write(b,0,n);}catch(Exception ignored){}
    }
    private void toastError(String m){Toast.makeText(this,m,Toast.LENGTH_LONG).show();}
    @Override protected void onDestroy(){worker.shutdownNow();super.onDestroy();}
}
