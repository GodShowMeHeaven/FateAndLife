import os
import yaml
from datetime import datetime

def collect_code(start_path: str, output_file: str) -> None:
    """Собирает основной код проекта и его зависимости в один файл"""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Записываем только критические метаданные
        project_info = {
            'name': 'FateAndLifeBot',
            'version': _get_version(start_path),
            'python_version': '3.10',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'main_modules': ['handlers', 'services', 'keyboards', 'tests', 'utils'],
            'dependencies': _get_dependencies(start_path)
        }
        
        outfile.write("# Project Metadata:\n'''\n")
        yaml.dump(project_info, outfile, allow_unicode=True)
        outfile.write("'''\n\n")
        
        # Записываем все конфигурационные файлы
        core_configs = ['config.yaml', 'user_data.yaml']
        configs = {
            name: _read_file(os.path.join(start_path, name))
            for name in core_configs 
            if os.path.exists(os.path.join(start_path, name))
        }
        
        if configs:
            outfile.write("# Core Configuration Files:\n'''\n")
            yaml.dump(configs, outfile, allow_unicode=True)
            outfile.write("'''\n\n")
        
        # Записываем все исходные файлы проекта
        core_modules = [
            'handlers/compatibility_fio.py',
            'handlers/compatibility_natal.py',
            'handlers/fortune.py',
            'handlers/horoscope.py',
            'handlers/natal_chart.py',
            'handlers/numerology.py',
            'handlers/subscription.py',
            'handlers/tarot.py',
            'handlers/user_profile.py',
            'keyboards/inline_buttons.py',
            'keyboards/main_menu.py',
            'services/compatibility_service.py',
            'services/database.py',
            'services/fortune_service.py',
            'services/horoscope_service.py',
            'services/natal_chart_service.py',
            'services/numerology_service.py',
            'services/openai_service.py',
            'services/tarot_service.py',
            'services/user_profile.py',
            'utils/pycache.py',
            'utils/zodiac.py'
        ]
        
        for module in core_modules:
            module_path = os.path.join(start_path, 'FateAndLifeBot', module)
            if os.path.exists(module_path):
                outfile.write(f"\n{'='*80}\n")
                outfile.write(f"# File: FateAndLifeBot/{module}\n")
                outfile.write(f"{'='*80}\n\n")
                outfile.write(_read_file(module_path))
                outfile.write("\n\n")
        
        # Записываем зависимости из requirements.txt
        requirements_file = os.path.join(start_path, 'requirements.txt')
        if os.path.exists(requirements_file):
            outfile.write("# Dependencies (from requirements.txt):\n'''\n")
            outfile.write(_read_file(requirements_file))
            outfile.write("'''\n\n")

def _get_version(path: str) -> str:
    """Получает версию из __init__.py"""
    try:
        init_path = os.path.join(path, 'FateAndLifeBot', '__init__.py')
        with open(init_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip("'").strip('"')
        return "0.1.0"  # Возвращаем значение по умолчанию, если версия не найдена
    except:
        return "0.1.0"  # Возвращаем значение по умолчанию при любой ошибке

def _get_dependencies(path: str) -> List[str]:
    """Получаем зависимости проекта из requirements.txt (если существует)"""
    requirements_file = os.path.join(path, 'requirements.txt')
    if os.path.exists(requirements_file):
        return _read_file(requirements_file).splitlines()
    return []  # Если файл не найден, возвращаем пустой список

def _read_file(path: str) -> str:
    """Безопасное чтение файла"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"# Error reading file: {str(e)}\n"

if __name__ == "__main__":
    project_root = "."
    output_file = "full_project_code.txt"
    collect_code(project_root, output_file)
    print(f"Core code collection complete. Check {output_file}")
