# NVIDIA NIM Integration Guide

Complete guide for using NVIDIA NIM (NVIDIA Inference Microservices) with the Human Factors Analysis Platform.

## Overview

NVIDIA NIM provides access to state-of-the-art LLMs including:
- **Llama 3.1 70B Instruct** (Default) - Excellent balance of performance and speed
- **Llama 3.1 405B Instruct** - Maximum capability for complex analysis
- **Llama 3.1 8B Instruct** - Fast, lightweight option
- And many other models from Meta, Mistral, Microsoft, etc.

## Benefits of NVIDIA NIM

✅ **High Performance**: Optimized inference with TensorRT-LLM  
✅ **Streaming Support**: Real-time response generation  
✅ **Cost Effective**: Competitive pricing  
✅ **OpenAI-Compatible API**: Easy integration  
✅ **Multiple Models**: Choose the right model for your needs

## Setup Instructions

### 1. Get NVIDIA API Key

1. Visit [NVIDIA API Catalog](https://build.nvidia.com/)
2. Sign up or log in with your NVIDIA account
3. Navigate to the model you want to use (e.g., Llama 3.1 70B)
4. Click "Get API Key" or "Generate Key"
5. Copy your API key (starts with `nvapi-...`)

### 2. Configure the Platform

Edit your `backend/.env` file:

```bash
# Set NVIDIA as your LLM provider
LLM_PROVIDER=nvidia

# Add your NVIDIA API key
NVIDIA_API_KEY=nvapi-YOUR_KEY_HERE

# Optional: Choose a different model (default is llama-3.1-70b-instruct)
NVIDIA_MODEL=meta/llama-3.1-70b-instruct
```

### 3. Available Models

You can use any of these models by setting `NVIDIA_MODEL`:

**Llama Models:**
```bash
# Recommended for most use cases
NVIDIA_MODEL=meta/llama-3.1-70b-instruct

# Maximum capability (slower, more expensive)
NVIDIA_MODEL=meta/llama-3.1-405b-instruct

# Fast and lightweight
NVIDIA_MODEL=meta/llama-3.1-8b-instruct
```

**Other Models:**
```bash
# Mistral Large
NVIDIA_MODEL=mistralai/mistral-large

# Microsoft Phi-3
NVIDIA_MODEL=microsoft/phi-3-medium-128k-instruct

# Mixtral 8x7B
NVIDIA_MODEL=mistralai/mixtral-8x7b-instruct-v0.1
```

See the full list at: https://build.nvidia.com/explore/discover

## Usage

### Basic Usage

Once configured, the platform automatically uses NVIDIA NIM:

```bash
# Start the backend
cd backend
python app.py
```

The backend will:
1. Initialize NVIDIA NIM client with your API key
2. Use streaming for real-time response generation
3. Apply NVIDIA-recommended parameters (temperature=0.2, top_p=0.7)

### API Example

```python
from llm_analyzer import LLMErgonomicAnalyzer

# Initialize with NVIDIA provider
analyzer = LLMErgonomicAnalyzer(
    provider="nvidia",
    api_key="nvapi-YOUR_KEY_HERE"  # Or set via NVIDIA_API_KEY env var
)

# Generate insights (automatically uses streaming)
insights = analyzer.generate_insights(
    ergonomic_metrics=metrics,
    image_context="Office worker at desk"
)

print(insights['executive_summary'])
```

### Direct API Usage

If you want to use NVIDIA NIM directly:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="nvapi-YOUR_KEY_HERE"
)

# Streaming completion
completion = client.chat.completions.create(
    model="meta/llama-3.1-70b-instruct",
    messages=[
        {"role": "system", "content": "You are an expert ergonomist."},
        {"role": "user", "content": "Analyze this posture..."}
    ],
    temperature=0.2,
    top_p=0.7,
    max_tokens=2048,
    stream=True
)

for chunk in completion:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

## Configuration Options

### Temperature & Top-P

The platform uses NVIDIA-recommended settings:

```python
temperature=0.2  # Lower = more focused, deterministic
top_p=0.7        # Nucleus sampling threshold
```

You can adjust these in `llm_analyzer.py` if needed.

### Max Tokens

Default: 2048 tokens (sufficient for comprehensive ergonomic analysis)

Increase if you need longer responses:
```python
max_tokens=4096  # For very detailed analysis
```

### Streaming

Streaming is enabled by default for NVIDIA to provide real-time feedback. The backend collects the full response before returning.

## Model Selection Guide

| Model | Best For | Speed | Quality | Cost |
|-------|----------|-------|---------|------|
| Llama 3.1 8B | Quick analysis, high volume | ⚡⚡⚡ | ⭐⭐⭐ | $ |
| Llama 3.1 70B | **Recommended** - Balanced | ⚡⚡ | ⭐⭐⭐⭐ | $$ |
| Llama 3.1 405B | Maximum accuracy | ⚡ | ⭐⭐⭐⭐⭐ | $$$ |

## Troubleshooting

### Error: "Invalid API Key"

**Solution**: Verify your API key is correct and active
```bash
# Test your API key
curl -X POST "https://integrate.api.nvidia.com/v1/chat/completions" \
  -H "Authorization: Bearer nvapi-YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta/llama-3.1-70b-instruct",
    "messages": [{"role":"user","content":"Hello"}],
    "max_tokens": 10
  }'
```

### Error: "Model not found"

**Solution**: Check the model name is correct. Visit https://build.nvidia.com/explore/discover for available models.

### Slow Response Times

**Solutions**:
1. Use a smaller model (e.g., llama-3.1-8b-instruct)
2. Reduce `max_tokens`
3. Check your network connection

### Rate Limiting

NVIDIA NIM has rate limits. If you hit them:
1. Add retry logic with exponential backoff
2. Reduce request frequency
3. Consider upgrading your plan

## Cost Optimization

### Tips to Reduce Costs

1. **Use the right model**: Start with 70B, only use 405B when necessary
2. **Optimize prompts**: Be concise to reduce token usage
3. **Cache results**: Store insights for similar postures
4. **Batch processing**: Analyze multiple images in one session

### Estimated Costs

Approximate costs per 1000 ergonomic analyses:

- **Llama 3.1 8B**: ~$0.20
- **Llama 3.1 70B**: ~$0.88
- **Llama 3.1 405B**: ~$5.32

(Prices subject to change - check NVIDIA pricing)

## Advanced Features

### Custom System Prompts

Modify the system prompt in `llm_analyzer.py`:

```python
messages=[
    {"role": "system", "content": "Custom instructions here..."},
    {"role": "user", "content": prompt}
]
```

### Multiple Providers

Switch between providers easily:

```bash
# Use NVIDIA
LLM_PROVIDER=nvidia

# Switch to OpenAI
LLM_PROVIDER=openai

# Switch to Anthropic
LLM_PROVIDER=anthropic
```

### Model Comparison

Compare different models on the same data:

```python
providers = ["nvidia", "openai", "anthropic"]
results = {}

for provider in providers:
    analyzer = LLMErgonomicAnalyzer(provider=provider)
    results[provider] = analyzer.generate_insights(metrics)

# Compare insights
for provider, insights in results.items():
    print(f"\n{provider.upper()}:")
    print(insights['executive_summary'])
```

## Support & Resources

- **NVIDIA NIM Documentation**: https://docs.nvidia.com/nim/
- **API Catalog**: https://build.nvidia.com/
- **Model Cards**: Detailed info on each model's capabilities
- **Community Forum**: https://forums.developer.nvidia.com/

## Example Output

With NVIDIA Llama 3.1 70B, you'll get comprehensive ergonomic analysis:

```
Executive Summary:
The analyzed posture shows moderate ergonomic concerns with a neck 
flexion of 35.2° (medium risk) and forward lean of 28.4° (medium risk). 
Immediate adjustments to monitor height and chair positioning are 
recommended to prevent long-term musculoskeletal issues.

Detailed Findings:
Head/Neck: Forward flexion angle of 35.2° exceeds the optimal range 
(<20°), indicating the monitor may be positioned too low...

[Full detailed analysis continues...]
```

## Migration from Other Providers

### From OpenAI

Simply change:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

To:
```bash
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
```

No code changes needed!

### From Anthropic

Same process - just update environment variables. The platform handles all provider differences automatically.

## Best Practices

1. **Start with default settings**: The platform uses optimized parameters
2. **Monitor costs**: Track API usage in NVIDIA dashboard
3. **Test different models**: Find the best balance for your use case
4. **Use streaming**: Provides better user experience
5. **Handle errors gracefully**: Implement retry logic for production

## Conclusion

NVIDIA NIM provides a powerful, cost-effective LLM solution for the Human Factors Analysis Platform. With streaming support and multiple model options, you can choose the right balance of speed, quality, and cost for your research needs.

For questions or issues, refer to the main platform documentation or NVIDIA's support resources.
