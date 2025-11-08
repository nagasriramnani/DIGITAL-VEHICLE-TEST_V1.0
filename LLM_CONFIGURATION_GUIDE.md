# LLM Configuration Guide

## Overview

The VTA system now reads LLM configuration from your `.env` file. You can configure whether to use a mock LLM (for testing) or a real HuggingFace model (for production).

---

## Configuration in `.env` File

Add these settings to your `.env` file:

```env
# ============================================================================
# LLM Configuration
# ============================================================================
# Set to false to use real HuggingFace models (requires LangChain + transformers)
USE_MOCK_LLM=true

# HuggingFace model ID (used when USE_MOCK_LLM=false)
# Examples:
#   - mock-llm (for testing)
#   - gpt2 (small, fast, good for testing)
#   - mistralai/Mistral-7B-v0.1 (7B parameters, good balance)
#   - meta-llama/Llama-2-7b-chat-hf (7B parameters, chat-optimized)
#   - TinyLlama/TinyLlama-1.1B-Chat-v1.0 (1.1B parameters, very fast)
HF_LLM_MODEL_ID=mock-llm

# Device for model inference (auto/cuda/cpu)
# 'auto' will use GPU if available, otherwise CPU
HF_DEVICE=auto

# Enable 8-bit quantization (reduces memory, requires bitsandbytes)
HF_LOAD_8BIT=false

# Generation parameters
HF_MAX_NEW_TOKENS=512
HF_TEMPERATURE=0.2
```

---

## Configuration Options

### `USE_MOCK_LLM`
- **Type**: `boolean` (true/false)
- **Default**: `true`
- **Description**: 
  - `true`: Uses a mock LLM with rule-based responses (good for testing, no dependencies)
  - `false`: Uses a real HuggingFace model (requires LangChain + transformers)

### `HF_LLM_MODEL_ID`
- **Type**: `string`
- **Default**: `mock-llm`
- **Description**: HuggingFace model identifier
- **Examples**:
  - `mock-llm` - Mock LLM for testing
  - `gpt2` - Small model (124M params), good for testing
  - `mistralai/Mistral-7B-v0.1` - Medium model (7B params)
  - `meta-llama/Llama-2-7b-chat-hf` - Chat-optimized (7B params)
  - `TinyLlama/TinyLlama-1.1B-Chat-v1.0` - Very fast (1.1B params)

### `HF_DEVICE`
- **Type**: `string`
- **Default**: `auto`
- **Options**: `auto`, `cuda`, `cpu`
- **Description**: Device for model inference
  - `auto`: Automatically detects and uses GPU if available
  - `cuda`: Force GPU usage
  - `cpu`: Force CPU usage

### `HF_LOAD_8BIT`
- **Type**: `boolean` (true/false)
- **Default**: `false`
- **Description**: Enable 8-bit quantization to reduce memory usage
- **Note**: Requires `bitsandbytes` package

### `HF_MAX_NEW_TOKENS`
- **Type**: `integer`
- **Default**: `512`
- **Range**: 1-4096
- **Description**: Maximum number of tokens to generate in response

### `HF_TEMPERATURE`
- **Type**: `float`
- **Default**: `0.2`
- **Range**: 0.0-2.0
- **Description**: Sampling temperature (lower = more deterministic, higher = more creative)

---

## Quick Setup

### Option 1: Use Mock LLM (Recommended for Testing)

Add to your `.env`:
```env
USE_MOCK_LLM=true
HF_LLM_MODEL_ID=mock-llm
```

**Pros**:
- ✅ No additional dependencies
- ✅ Fast startup
- ✅ Works immediately
- ✅ Good for testing

**Cons**:
- ❌ Limited responses (rule-based)
- ❌ Not production-ready

### Option 2: Use Real HuggingFace Model (Production)

**Step 1**: Install dependencies
```bash
pip install langchain langchain-core transformers accelerate
```

**Step 2**: Add to your `.env`:
```env
USE_MOCK_LLM=false
HF_LLM_MODEL_ID=gpt2
HF_DEVICE=auto
HF_LOAD_8BIT=false
HF_MAX_NEW_TOKENS=512
HF_TEMPERATURE=0.2
```

**Pros**:
- ✅ Real AI responses
- ✅ More intelligent conversations
- ✅ Production-ready

**Cons**:
- ❌ Requires more dependencies
- ❌ Slower startup (model loading)
- ❌ May require GPU for larger models

---

## Model Recommendations

### For Testing (Small Models)
- **`gpt2`**: 124M parameters, very fast, good for testing
- **`TinyLlama/TinyLlama-1.1B-Chat-v1.0`**: 1.1B parameters, chat-optimized

### For Production (Medium Models)
- **`mistralai/Mistral-7B-v0.1`**: 7B parameters, good balance
- **`meta-llama/Llama-2-7b-chat-hf`**: 7B parameters, chat-optimized

### For High Performance (Large Models)
- **`meta-llama/Llama-2-13b-chat-hf`**: 13B parameters (requires more GPU memory)
- **`mistralai/Mixtral-8x7B-Instruct-v0.1`**: Mixture of experts (requires significant GPU memory)

---

## Example `.env` Configurations

### Testing Configuration
```env
USE_MOCK_LLM=true
HF_LLM_MODEL_ID=mock-llm
```

### Development Configuration (Small Model)
```env
USE_MOCK_LLM=false
HF_LLM_MODEL_ID=gpt2
HF_DEVICE=auto
HF_LOAD_8BIT=false
HF_MAX_NEW_TOKENS=256
HF_TEMPERATURE=0.3
```

### Production Configuration (Medium Model)
```env
USE_MOCK_LLM=false
HF_LLM_MODEL_ID=mistralai/Mistral-7B-v0.1
HF_DEVICE=cuda
HF_LOAD_8BIT=true
HF_MAX_NEW_TOKENS=512
HF_TEMPERATURE=0.2
```

---

## How It Works

1. **Settings Loading**: The system reads `.env` file on startup
2. **Configuration**: `src/config/settings.py` loads LLM settings
3. **LLM Manager**: `src/orchestrators/llm_setup.py` uses settings to initialize LLM
4. **Agent Creation**: `src/orchestrators/vta_agent.py` creates agent with configured LLM

---

## Verification

After updating your `.env` file, restart the API server:

```bash
uvicorn src.api.main:app --reload --port 8000
```

You should see log messages indicating:
- Whether mock or real LLM is being used
- Which model is loaded
- Device being used (CPU/GPU)

---

## Troubleshooting

### Issue: "LangChain not available"
**Solution**: Install LangChain if you want to use real models:
```bash
pip install langchain langchain-core
```

### Issue: Model loading fails
**Solution**: 
1. Check if model ID is correct
2. Ensure you have enough disk space (models can be several GB)
3. Try a smaller model first (e.g., `gpt2`)

### Issue: Out of memory
**Solution**:
1. Use a smaller model
2. Enable 8-bit quantization: `HF_LOAD_8BIT=true`
3. Use CPU instead of GPU: `HF_DEVICE=cpu`

### Issue: Slow responses
**Solution**:
1. Use a smaller model
2. Reduce `HF_MAX_NEW_TOKENS`
3. Use GPU if available: `HF_DEVICE=cuda`

---

## Current Status

The system is configured to:
- ✅ Read LLM settings from `.env`
- ✅ Use mock LLM by default (no dependencies required)
- ✅ Support real HuggingFace models when configured
- ✅ Automatically detect GPU/CPU

**You can now configure the LLM in your `.env` file!** 🎉

