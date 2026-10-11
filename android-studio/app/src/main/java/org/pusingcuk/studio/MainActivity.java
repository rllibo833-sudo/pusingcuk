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
import android.widget.Button;
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

public final class MainActivity extends Activity {
    private static final int MAX_SOURCE_BYTES = 64 * 1024, MAX_STDIN_BYTES = 16 * 1024;
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private EditText source, stdin;
    private TextView output, status;
    private Button runButton;
    private File runtime, projectFile;

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
        getWindow().setStatusBarColor(Color.rgb(10,15,28)); getWindow().setNavigationBarColor(Color.rgb(10,15,28));
        File dir = new File(getFilesDir(), "projects"); if (!dir.exists()) dir.mkdirs();
        projectFile = new File(dir, "program.pusingcuk"); buildUi(); installRuntime(); loadProject();
    }

    private void buildUi() {
        ScrollView scroll = new ScrollView(this); scroll.setFillViewport(true); scroll.setBackgroundColor(Color.rgb(10,16,32));
        LinearLayout page = column(); scroll.addView(page); setContentView(scroll);
        TextView title = label("Pusingcuk Studio",23,Color.rgb(98,214,181)); title.setTypeface(Typeface.DEFAULT,Typeface.BOLD); page.addView(title);
        page.addView(label("Editor + runtime native · Android",13,Color.LTGRAY));
        LinearLayout actions = column(); actions.setPadding(0,dp(2),0,dp(2)); page.addView(actions);
        runButton = button("▶ Jalankan",actions,v->runProgram());
        button("Simpan proyek",actions,v->saveProject());
        button("Buka proyek lokal",actions,v->loadProject());
        button("Impor file publik dari GitHub",actions,v->showGitHubImport());
        button("Bagikan / ekspor kode",actions,v->shareProject());
        page.addView(label("program.pusingcuk",16,Color.WHITE));
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
            status.setText("Runtime native siap · "+abi);
            source.setText("jancuk\nlah nama = \"Dunia\"\n\nfungsi tambah(a, b)\n    balek a + b\nselesai fungsi\n\nhedeh \"Halo, \" + nama\nhedeh tambah(20, 22)\nselesai jancuk");
        } catch(Exception e) { status.setText("Runtime gagal disiapkan: "+e.getMessage()); runButton.setEnabled(false); }
    }

    private void saveProject() {
        try {
            String code=source.getText().toString(); if(utf8Length(code)>MAX_SOURCE_BYTES) throw new IllegalArgumentException("Kode melebihi 64 KiB.");
            try(FileOutputStream out=new FileOutputStream(projectFile)){out.write(code.getBytes(StandardCharsets.UTF_8));}
            Toast.makeText(this,"Tersimpan di proyek lokal aplikasi",Toast.LENGTH_SHORT).show();
        } catch(Exception e){toastError("Gagal menyimpan: "+e.getMessage());}
    }
    private void loadProject() {
        try {
            if(projectFile==null||!projectFile.isFile()) { if(source!=null&&source.length()==0) source.setText("jancuk\nhedeh \"Halo, dunia!\"\nselesai jancuk"); return; }
            try(FileInputStream in=new FileInputStream(projectFile); ByteArrayOutputStream out=new ByteArrayOutputStream()) {
                byte[] b=new byte[4096]; int n; while((n=in.read(b))!=-1)out.write(b,0,n);
                source.setText(new String(out.toByteArray(),StandardCharsets.UTF_8));
            }
            status.setText("Proyek lokal dibuka");
        } catch(Exception e){toastError("Gagal membuka proyek: "+e.getMessage());}
    }

    private void runProgram() {
        final String code=source.getText().toString(), input=stdin.getText().toString();
        if(runtime==null||!runtime.canExecute()){toastError("Runtime native belum siap.");return;}
        if(code.trim().isEmpty()){toastError("Kode tidak boleh kosong.");return;}
        if(utf8Length(code)>MAX_SOURCE_BYTES){toastError("Kode maksimum 64 KiB.");return;}
        if(utf8Length(input)>MAX_STDIN_BYTES){toastError("Input maksimum 16 KiB.");return;}
        runButton.setEnabled(false); status.setText("Program sedang berjalan…"); output.setText("");
        worker.execute(()->{
            File program=null; Process proc=null; ByteArrayOutputStream stdout=new ByteArrayOutputStream(), stderr=new ByteArrayOutputStream();
            try {
                File work=new File(getCacheDir(),"run"); if(!work.exists()&&!work.mkdirs())throw new IllegalStateException("Folder sementara gagal dibuat.");
                program=File.createTempFile("program-",".pusingcuk",work);
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
                final String outText=stdout.toString("UTF-8"),errText=stderr.toString("UTF-8");
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

    private void showGitHubImport() {
        LinearLayout form=column();form.setPadding(dp(18),0,dp(18),0);
        EditText owner=editor("Pemilik repo",1);owner.setText("rllibo833-sudo");
        EditText repo=editor("Nama repo",1);repo.setText("pusingcuk");
        EditText path=editor("Path file .pusingcuk",1);path.setText("examples/native/rekap_anggaran.pusingcuk");
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
        Intent intent=new Intent(Intent.ACTION_SEND);intent.setType("text/plain");intent.putExtra(Intent.EXTRA_SUBJECT,"program.pusingcuk");intent.putExtra(Intent.EXTRA_TEXT,code);
        startActivity(Intent.createChooser(intent,"Bagikan kode Pusingcuk"));
    }
    private static int utf8Length(String s){return s.getBytes(StandardCharsets.UTF_8).length;}
    private static void copy(InputStream in,ByteArrayOutputStream out){
        try(InputStream input=in){byte[] b=new byte[4096];int n;while((n=input.read(b))!=-1)synchronized(out){out.write(b,0,n);}}catch(Exception ignored){}
    }
    private void toastError(String m){Toast.makeText(this,m,Toast.LENGTH_LONG).show();}
    @Override protected void onDestroy(){worker.shutdownNow();super.onDestroy();}
}
