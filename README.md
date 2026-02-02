# Image Data Extraction Tool

Extract Email, First name, and Name from images using GPT-4 Vision and save to CSV.

## 📋 Overview

This tool uses OpenAI's GPT-4 Vision API to extract structured data from images containing tables. It's built with Clean Architecture principles, featuring:

- **Modular design**: Separated concerns across models, services, and utilities
- **Type safety**: Full type hints throughout
- **Error handling**: Custom exception hierarchy
- **Logging**: Structured logging with Python's logging module
- **Testing**: 94% test coverage with pytest
- **English codebase**: Internationalized for global use

## 📁 Project Structure

```
VisionParser/
├── main.py                         # Main entry point
├── models/                         # Configuration models
│   ├── __init__.py
│   ├── env_config.py              # Environment variable management
│   ├── image_folder_config.py     # Image folder management
│   ├── openai_config.py           # OpenAI API configuration
│   └── app_config.py              # Application config (Facade)
├── services/                       # Business logic
│   ├── __init__.py
│   ├── extractor.py               # Image data extraction service
│   └── processor.py               # Batch processing service
├── utils/                          # Utilities
│   ├── __init__.py
│   └── image_utils.py             # Image encoding utilities
├── tests/                          # Test suite (50 tests, 94% coverage)
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_services.py
│   ├── test_utils.py
│   └── test_main.py
├── .env                            # Environment variables (API keys)
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── pytest.ini                      # Pytest configuration
├── TESTING.md                      # Testing documentation
├── images/                         # Input images folder
└── extracted_data_gpt_all.csv      # Output CSV file
```

## 🏗️ Architecture

### Clean Architecture Layers

#### 1. **Models Layer** (`models/`)
Configuration and data models with validation.

**EnvConfig** - Environment variable management:
```python
from models import EnvConfig

env = EnvConfig(".env")
api_key = env.get_openai_api_key()  # Validated retrieval
```

**ImageFolderConfig** - Image folder management:
```python
from models import ImageFolderConfig

images = ImageFolderConfig("images")
images.validate()
image_files = images.get_image_files()  # List[Path]
```

**OpenAIConfig** - OpenAI API configuration:
```python
from models import OpenAIConfig

openai = OpenAIConfig(
    api_key="sk-...",
    model="gpt-4o",
    max_tokens=2000,
    temperature=0.0
)
```

**Config** - Application configuration (Facade Pattern):
```python
from models import Config

config = Config()
config.validate()

# Access sub-configurations
api_key = config.openai.api_key
image_files = config.images.get_image_files()
```

#### 2. **Services Layer** (`services/`)
Business logic for data extraction and processing.

**ImageDataExtractor** - GPT-4 Vision integration:
```python
from services.extractor import ImageDataExtractor

extractor = ImageDataExtractor(client, config)
records = extractor.extract_all_info("image.png")
```

**DataProcessor** - Batch processing:
```python
from services.processor import DataProcessor

processor = DataProcessor(extractor, output_file, fields)
result = processor.process_images(image_files)
processor.save_to_csv(result.all_results)
processor.log_summary(result)
```

#### 3. **Utils Layer** (`utils/`)
Utility functions.

```python
from utils.image_utils import encode_image

base64_string = encode_image("image.png")
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install packages from requirements.txt
pip install -r requirements.txt

# Or install manually
pip install openai python-dotenv pillow
```

### 2. Configure API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-proj-...
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Add Images

```bash
# Create images folder
mkdir images

# Add image files (.png, .jpg, .jpeg, .bmp, .tiff)
cp your_images/*.png images/
```

### 4. Run

```bash
python main.py
```

Output will be saved to `extracted_data_gpt_all.csv`.

## 📝 Usage

### Basic Usage

```bash
python main.py
```

### Custom Configuration

```python
from models import Config
from openai import OpenAI
from services.extractor import ImageDataExtractor
from services.processor import DataProcessor

# Initialize with custom settings
config = Config(
    env_file=".env.production",
    images_folder="my_images",
    output_file="results.csv",
    extract_fields=["filename", "email", "firstname", "name"]
)

# Initialize services
client = OpenAI(api_key=config.openai.api_key)
extractor = ImageDataExtractor(client, config)
processor = DataProcessor(extractor, config.output_file, config.extract_fields)

# Process images
image_files = config.images.get_image_files()
result = processor.process_images(image_files)

# Save results
processor.save_to_csv(result.all_results)
processor.log_summary(result)
```

## 🧪 Testing

Comprehensive test suite with 94% coverage.

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=models --cov=services --cov=utils --cov=main --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=models --cov=services --cov=utils --cov=main --cov-report=html
# Open htmlcov/index.html
```

### Test Coverage

| Module                          | Coverage |
|---------------------------------|----------|
| models/env_config.py            | 97%      |
| models/image_folder_config.py   | 97%      |
| models/openai_config.py         | 96%      |
| models/app_config.py            | 94%      |
| services/extractor.py           | 98%      |
| services/processor.py           | 85%      |
| utils/image_utils.py            | 100%     |
| main.py                         | 98%      |
| **Overall**                     | **94%**  |

See [TESTING.md](TESTING.md) for detailed testing documentation.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-proj-your-api-key-here
```

### Config Class

```python
from models import Config

config = Config(
    env_file=".env",                    # Environment file path
    images_folder="images",             # Image folder path
    output_file="output.csv",           # Output CSV filename
    extract_fields=["filename", "email", "firstname", "name"]  # Fields to extract
)

# Validate configuration
config.validate()

# Access sub-configs
config.env          # EnvConfig instance
config.images       # ImageFolderConfig instance
config.openai       # OpenAIConfig instance
```

### Customization

**Change OpenAI model:**
```python
config.openai.model = "gpt-4-turbo"
config.openai.max_tokens = 3000
config.openai.temperature = 0.5
```

**Change image folder:**
```python
config.images.folder_path = "other_images"
```

**Custom extraction fields:**
```python
config = Config(
    extract_fields=["filename", "email", "name"]  # Exclude firstname
)
```

## 🚨 Error Handling

Custom exception hierarchy:

### Environment Errors
- `EnvConfigError`: Base environment error
- `OpenAIKeyNotFoundError`: API key not found
- `OpenAIKeyInvalidError`: API key invalid

### Image Folder Errors
- `ImageFolderConfigError`: Base folder error
- `ImageFolderNotFoundError`: Folder doesn't exist
- `NoImageFilesError`: No images found

### OpenAI Config Errors
- `OpenAIConfigError`: Base config error
- `InvalidMaxTokensError`: Invalid max_tokens value
- `InvalidTemperatureError`: Invalid temperature value

### Processing Errors
- `ImageProcessingError`: Image processing failed
- `OpenAIAPIError`: OpenAI API call failed

Example:
```python
from models import Config
from models.env_config import OpenAIKeyNotFoundError

try:
    config = Config()
    config.validate()
except OpenAIKeyNotFoundError:
    print("Please set OPENAI_API_KEY in .env file")
except Exception as e:
    print(f"Configuration error: {e}")
```

## 📊 Output

Results are saved to CSV with the following fields:

| Field      | Description        |
|------------|--------------------|
| filename   | Source image name  |
| email      | Email address      |
| firstname  | First name         |
| name       | Full name          |

Example output:
```csv
filename,email,firstname,name
image1.png,john@example.com,John,John Doe
image1.png,jane@example.com,Jane,Jane Smith
image2.png,bob@example.com,Bob,Bob Johnson
```

## 🔧 Development

### Install Development Dependencies

```bash
# Using requirements.txt (already includes test dependencies)
pip install -r requirements.txt

# Or install test dependencies separately
pip install pytest pytest-cov
```

### Run Tests

```bash
pytest tests/ -v
```

### Code Style

- Type hints throughout
- Docstrings for all classes and methods
- English comments and messages
- Logging instead of print statements
- Clean Architecture principles

## 📝 Supported Image Formats

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- BMP (`.bmp`)
- TIFF (`.tiff`)

## 💰 Cost

This tool uses OpenAI's GPT-4 Vision API which is a paid service. Costs depend on:
- Number of images
- Image size
- Max tokens setting

Refer to [OpenAI Pricing](https://openai.com/pricing) for current rates.

## ⚠️ Notes

- **Processing time**: GPT-4 Vision API calls take time; be patient with large batches
- **API limits**: Respect OpenAI's rate limits
- **Image quality**: Higher quality images yield better results
- **Table structure**: Works best with clear, well-formatted tables

## 📄 License

MIT

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure tests pass: `pytest tests/`
5. Submit a pull request

## 📚 Additional Documentation

- [TESTING.md](TESTING.md) - Comprehensive testing guide
- [.env.example](.env.example) - Environment variables template

## 🐛 Troubleshooting

### "OPENAI_API_KEY is not set"
Create a `.env` file with your API key:
```bash
echo "OPENAI_API_KEY=sk-your-key" > .env
```

### "Image folder not found"
Create the images folder and add images:
```bash
mkdir images
cp your_images/*.png images/
```

### "No image files found"
Ensure your images have supported extensions (.png, .jpg, .jpeg, .bmp, .tiff).

### Import errors
Make sure you're in the virtual environment:
```bash
source .venv/bin/activate  # macOS/Linux
```

## 📞 Support

For issues or questions, please:
1. Check the troubleshooting section
2. Review [TESTING.md](TESTING.md)
3. Check existing issues on GitHub
4. Create a new issue with details
