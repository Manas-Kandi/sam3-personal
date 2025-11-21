# Quick Start: NVIDIA NIM

Get up and running with NVIDIA NIM in 5 minutes.

## 1. Get API Key (2 minutes)

1. Go to https://build.nvidia.com/
2. Sign up/login
3. Click "Get API Key" on any model
4. Copy your key (starts with `nvapi-`)

## 2. Configure (1 minute)

Edit `backend/.env`:

```bash
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-YOUR_KEY_HERE
NVIDIA_MODEL=meta/llama-3.1-70b-instruct
```

## 3. Test (1 minute)

```bash
cd backend
python test_nvidia.py
```

Should see: ✅ Success! NVIDIA NIM is working correctly.

## 4. Run (1 minute)

```bash
# Terminal 1 - Backend
python app.py

# Terminal 2 - Frontend
cd ../frontend
npm run dev
```

## 5. Use

Open http://localhost:5173 and upload an image!

---

## Troubleshooting

**"Command not found: python"**
→ Use `python3` instead

**"Invalid API key"**
→ Check key in .env matches your NVIDIA dashboard

**"Model not found"**
→ Verify model name: `meta/llama-3.1-70b-instruct`

---

## Model Options

Change `NVIDIA_MODEL` in `.env`:

- `meta/llama-3.1-8b-instruct` - Fast ⚡⚡⚡
- `meta/llama-3.1-70b-instruct` - **Balanced** ⚡⚡ (Default)
- `meta/llama-3.1-405b-instruct` - Best quality ⚡

---

## Full Documentation

- **Detailed Setup**: [NVIDIA_NIM_SETUP.md](NVIDIA_NIM_SETUP.md)
- **Implementation**: [NVIDIA_IMPLEMENTATION_SUMMARY.md](NVIDIA_IMPLEMENTATION_SUMMARY.md)
- **General Setup**: [SETUP.md](SETUP.md)

---

**Need help?** Check the troubleshooting section in NVIDIA_NIM_SETUP.md
