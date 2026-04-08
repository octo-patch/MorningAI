"""Entity registry for morning-ai.

Maps all 76+ tracked entities to their information sources across platforms.
Derived from morning-ai/entities/*.md definitions.
"""

# X/Twitter handles per entity (without @)
X_HANDLES = {
    # === Frontier Labs ===
    "OpenAI": ["OpenAI", "ChatGPTapp", "sama", "markchen90", "gdb", "nickturley"],
    "Anthropic": ["AnthropicAI", "claudeai", "claude_code", "DarioAmodei", "alexalbert__", "bcherny", "trq212"],
    "Google DeepMind": ["GoogleDeepMind", "GoogleAI", "GoogleAIStudio", "GeminiApp", "JeffDean", "OfficialLoganK"],
    "Meta AI": ["AIatMeta", "ylecun"],
    "xAI": ["xai", "elonmusk"],
    "Microsoft": ["Microsoft", "MSFTCopilot", "OpenAtMicrosoft"],

    # === Model & Infrastructure ===
    "NVIDIA": ["nvidia", "NVIDIAAIDev", "DrJimFan"],
    "Mistral AI": ["MistralAI", "arthurmensch"],
    "Cohere": ["cohere"],
    "Perplexity AI": ["perplexity_ai", "AravSrinivas", "DenisYarats"],
    "Amazon AWS": ["awscloud"],
    "Together AI": ["togethercomputer"],
    "Groq": ["GroqInc"],
    # Apple has no AI-specific X account

    # === China AI ===
    "Qwen (Alibaba)": ["Alibaba_Qwen"],
    "DeepSeek": ["deepseek_ai"],
    "Doubao (ByteDance)": ["doubaoAi"],
    "GLM (Zhipu)": ["Zai_org"],
    "Kimi (Moonshot)": ["Kimi_Moonshot"],
    "MiniMax": ["MiniMax_AI", "MiniMaxAI"],
    "Kling (Kuaishou)": ["Kling_ai", "AiKling"],
    "InternLM (Shanghai AI Lab)": ["Shanghai_AI_Lab"],
    "LongCat (Meituan)": ["Meituan_LongCat"],
    "01.AI": ["01ai_yi"],
    "Baichuan": ["Baichuan_AI"],
    "StepFun": ["StepFunAI"],
    "Tencent Hunyuan": ["TencentHunyuan", "TXhunyuan"],

    # === Coding Tools ===
    "Cursor": ["cursor_ai", "mntruell", "ericzakariasson"],
    "Cline": ["cline", "sdrzn", "nickbaumann_"],
    "OpenCode": ["thdxr", "fanjiewang"],
    "Droid (Factory AI)": ["FactoryAI"],
    "OpenClaw": ["openclaw", "steipete"],
    "Windsurf": ["windsurf"],
    "Augment Code": ["AugmentCode"],
    # Aider has no official X account
    "Devin (Cognition)": ["cognition"],
    "browser-use": ["browser_use", "gregpr07", "larsencc"],

    # === AI Apps ===
    "v0 (Vercel)": ["v0", "rauchg"],
    "bolt.new": ["boltdotnew", "EricSimons"],
    "Lovable": ["Lovable", "antonosika", "felixhhaas"],
    "Replit": ["Replit", "amasad"],
    "Lovart": ["lovart_ai", "Elena_Leung_29"],
    "Manus": ["ManusAI", "Red_Xiao_", "pelotonben"],
    "Genspark": ["genspark_ai", "ericjing_ai", "sang_wen"],
    "Character.ai": ["character_ai"],

    # === Vision & Media ===
    "Midjourney": ["midjourney", "DavidHolz"],
    "Runway": ["runwayml", "cpvalenzuela"],
    "Pika": ["pika_labs", "demi_chen"],
    "Luma AI": ["LumaLabsAI", "abolishingme"],
    "Lightricks": ["Lightricks"],
    "FLUX (BFL)": ["bfl_ml"],
    "Ideogram": ["ideaboramAI"],
    "Adobe Firefly": ["AdobeFirefly"],
    "Leonardo AI": ["LeonardoAi_"],
    "Stability AI": ["StabilityAI", "robrombach"],
    "ElevenLabs": ["elevenlabsio"],
    "Udio": ["udiomusic"],
    "Suno": ["SunoAIMusic"],

    # === Benchmarks ===
    "LMSYS": ["laboramsys"],
    "LMArena": ["arena"],
    "Artificial Analysis": ["ArtificialAnlys"],
    "HuggingFace": ["huggingface"],
    "Scale AI": ["scale_AI"],
    "vLLM": ["vllm_project"],
    "Replicate": ["replicate"],

    # === KOL ===
    "Andrej Karpathy": ["karpathy"],
    "AK": ["_akhaliq"],
    "Andrew Ng": ["AndrewYNg"],
    "Rowan Cheung": ["rowancheung"],
    "Ben Tossell": ["bentossell"],
    "Elie Bakouch": ["eliebakouch"],
    "Swyx": ["swyx"],
    "Simon Willison": ["simonw"],
}

# GitHub orgs/repos per entity
GITHUB_SOURCES = {
    # Frontier Labs
    "OpenAI": {"orgs": ["openai"], "repos": []},
    "Anthropic": {"orgs": ["anthropics"], "repos": ["anthropics/claude-code"]},
    "Google DeepMind": {"orgs": ["google-deepmind"], "repos": []},
    "Meta AI": {"orgs": ["meta-llama"], "repos": []},
    "xAI": {"orgs": ["xai-org"], "repos": []},
    "Microsoft": {"orgs": ["microsoft"], "repos": []},
    # Model & Infrastructure
    "NVIDIA": {"orgs": ["NVIDIA"], "repos": []},
    "Mistral AI": {"orgs": ["mistralai"], "repos": []},
    "Cohere": {"orgs": ["cohere-ai"], "repos": []},
    "Together AI": {"orgs": ["togethercomputer"], "repos": []},
    "Apple": {"orgs": ["ml-explore"], "repos": []},
    # China AI
    "Qwen (Alibaba)": {"orgs": ["QwenLM"], "repos": []},
    "DeepSeek": {"orgs": ["deepseek-ai"], "repos": []},
    "Doubao (ByteDance)": {"orgs": ["bytedance"], "repos": []},
    "GLM (Zhipu)": {"orgs": ["THUDM"], "repos": []},
    "Kimi (Moonshot)": {"orgs": ["MoonshotAI"], "repos": []},
    "MiniMax": {"orgs": ["MiniMax-AI"], "repos": []},
    "InternLM (Shanghai AI Lab)": {"orgs": ["InternLM"], "repos": []},
    "01.AI": {"orgs": ["01-ai"], "repos": []},
    "Baichuan": {"orgs": ["baichuan-inc"], "repos": []},
    "Tencent Hunyuan": {"orgs": ["Tencent-Hunyuan"], "repos": []},
    # Coding Tools
    "Cline": {"orgs": [], "repos": ["cline/cline"]},
    "OpenCode": {"orgs": [], "repos": ["sst/opencode"]},
    "OpenClaw": {"orgs": ["openclaw"], "repos": ["openclaw/openclaw"]},
    "Aider": {"orgs": [], "repos": ["Aider-AI/aider"]},
    "browser-use": {"orgs": [], "repos": ["browser-use/browser-use"]},
    # Vision & Media
    "FLUX (BFL)": {"orgs": ["black-forest-labs"], "repos": []},
    "Stability AI": {"orgs": ["Stability-AI"], "repos": []},
}

# HuggingFace author/org names per entity
HUGGINGFACE_AUTHORS = {
    # Frontier Labs
    "Google DeepMind": ["google"],
    "Meta AI": ["meta-llama"],
    "Microsoft": ["microsoft"],
    # Model & Infrastructure
    "NVIDIA": ["nvidia"],
    "xAI": ["xai-org"],
    "Mistral AI": ["mistralai"],
    "Cohere": ["CohereForAI"],
    "Apple": ["apple"],
    # China AI
    "DeepSeek": ["deepseek-ai"],
    "MiniMax": ["MiniMaxAI"],
    "Stability AI": ["stabilityai"],
    "Qwen (Alibaba)": ["Qwen"],
    "Doubao (ByteDance)": ["bytedance"],
    "GLM (Zhipu)": ["THUDM"],
    "InternLM (Shanghai AI Lab)": ["internlm"],
    "LongCat (Meituan)": ["meituan-longcat"],
    "01.AI": ["01-ai"],
    "Baichuan": ["baichuan-inc"],
    "Tencent Hunyuan": ["tencent", "Tencent-Hunyuan"],
    # Vision & Media
    "FLUX (BFL)": ["black-forest-labs"],
}

# arXiv search queries per entity
ARXIV_QUERIES = {
    "OpenAI": ["OpenAI"],
    "Anthropic": ["Anthropic"],
    "Google DeepMind": ["DeepMind"],
    "Meta AI": ["Meta AI", "FAIR"],
    "Microsoft": ["Microsoft AI", "Phi model"],
    "NVIDIA": ["NVIDIA AI"],
    "Mistral AI": ["Mistral AI"],
    "DeepSeek": ["DeepSeek"],
    "Qwen (Alibaba)": ["Qwen"],
    "GLM (Zhipu)": ["GLM", "ChatGLM"],
    "InternLM (Shanghai AI Lab)": ["InternLM"],
    "01.AI": ["Yi model"],
    "Baichuan": ["Baichuan"],
    "Tencent Hunyuan": ["Tencent Hunyuan", "Hunyuan"],
}

# Web search queries per entity (blog/changelog URLs)
WEB_QUERIES = {
    # Frontier Labs
    "OpenAI": ["site:openai.com/blog", "site:platform.openai.com/docs/changelog"],
    "Anthropic": ["site:anthropic.com/news", "site:docs.anthropic.com/en/release-notes"],
    "Google DeepMind": ["site:deepmind.google/discover/blog", "site:ai.google.dev/gemini-api/docs/changelog"],
    "Meta AI": ["site:ai.meta.com/blog"],
    "xAI": ["site:x.ai/blog"],
    "Microsoft": ["site:blogs.microsoft.com/ai"],
    # Model & Infrastructure
    "NVIDIA": ["site:blogs.nvidia.com AI"],
    "Mistral AI": ["site:mistral.ai/news"],
    "Cohere": ["site:cohere.com/blog"],
    "Perplexity AI": ["site:perplexity.ai/hub/blog"],
    "Amazon AWS": ["site:aws.amazon.com/blogs/machine-learning"],
    "Together AI": ["site:together.ai/blog"],
    "Groq": ["site:wow.groq.com/blog"],
    "Apple": ["site:machinelearning.apple.com"],
    # China AI
    "DeepSeek": ["site:deepseek.com", "site:api-docs.deepseek.com/updates"],
    "MiniMax": ["site:platform.minimaxi.com/docs/release-notes"],
    "Stability AI": ["site:stability.ai/news"],
    # Coding Tools
    "Cursor": ["site:cursor.com/changelog"],
    "OpenClaw": ["site:openclaws.io/blog", "site:openclawai.io/changelog"],
    "Windsurf": ["site:windsurf.com/changelog"],
    "Augment Code": ["site:augmentcode.com/blog"],
    # AI Apps
    "v0 (Vercel)": ["site:vercel.com/changelog"],
    "bolt.new": ["site:support.bolt.new/release-notes"],
    "Lovable": ["site:lovable.dev/changelog"],
    "Replit": ["site:docs.replit.com/updates"],
    # Vision & Media
    "Runway": ["site:runwayml.com/changelog"],
    "ElevenLabs": ["site:elevenlabs.io/blog"],
}

# Reddit search keywords per entity
REDDIT_KEYWORDS = {
    "OpenAI": ["OpenAI", "ChatGPT", "GPT-5"],
    "Anthropic": ["Anthropic", "Claude"],
    "Google DeepMind": ["Gemini", "DeepMind"],
    "Meta AI": ["Llama", "Meta AI"],
    "Microsoft": ["Copilot", "Phi model"],
    "NVIDIA": ["NVIDIA AI", "CUDA"],
    "xAI": ["Grok", "xAI"],
    "Mistral AI": ["Mistral"],
    "Cohere": ["Cohere", "Command R"],
    "Perplexity AI": ["Perplexity"],
    "DeepSeek": ["DeepSeek"],
    "MiniMax": ["MiniMax", "Hailuo"],
    "Tencent Hunyuan": ["Hunyuan", "Tencent AI"],
    "Stability AI": ["Stable Diffusion", "Stability AI"],
    "Qwen (Alibaba)": ["Qwen"],
    "Cursor": ["Cursor AI"],
    "Cline": ["Cline AI"],
    "Windsurf": ["Windsurf", "Codeium"],
    "OpenClaw": ["OpenClaw"],
    "Devin (Cognition)": ["Devin AI"],
}

# HN search keywords per entity
HN_KEYWORDS = {
    "OpenAI": ["OpenAI"],
    "Anthropic": ["Anthropic", "Claude"],
    "Google DeepMind": ["Gemini", "DeepMind"],
    "Meta AI": ["Llama", "Meta AI"],
    "Microsoft": ["Copilot", "Microsoft AI"],
    "Mistral AI": ["Mistral"],
    "DeepSeek": ["DeepSeek"],
    "Cursor": ["Cursor"],
    "Perplexity AI": ["Perplexity"],
}

# Discord announcement channels per entity
DISCORD_CHANNELS = {
    "Midjourney": "https://discord.gg/midjourney",
    "Stability AI": "https://discord.gg/stablediffusion",
    "Cursor": "https://discord.gg/cursor",
    "Cline": "https://discord.gg/cline",
}

# YouTube channel IDs per entity
YOUTUBE_CHANNELS = {
    "OpenAI": "UCXZCJLdBC09xxGZ6gcdrc6A",
    "Google DeepMind": "UCwF9VGMVhKiTTx1R1kZpWvg",
    "Anthropic": "UCi1_3SeJ_GlqkV9_FZcMdQg",
    "NVIDIA": "UCHuiy8bXnmK5nisYHKIIeFxA",
    "Microsoft": "UCFtEEv80fQVKkbn3ZiQHIHg",
}

