# ADAPTER HP+TERMUX -> PAKAI ENGINE ASLI REPO
import sys
sys.path.insert(0, ".")
try:
    from library.local_ai_provider import LocalAIProvider
    from library.assistant import Assistant
    provider = LocalAIProvider()
    assistant = Assistant(provider)
    prompt = " ".join(sys.argv[1:])
    out = assistant.generate(prompt)
    print(out)
except Exception as e:
    # fallback kalo Ollama mati
    import re
    p = " ".join(sys.argv[1:]).lower()
    nums = list(map(int, re.findall(r'\d+', p)))
    if nums and len(nums)>=2 and "tambah" in p:
        print(f'jancuk\nlah a = {nums[0]}\nlah b = {nums[1]}\nhedeh a + b\nselesai jancuk')
    else:
        print('jancuk\nlah nama = "Dunia"\nhedeh "Halo, " + nama\nselesai jancuk')
