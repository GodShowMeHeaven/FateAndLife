import os
import yaml
from typing import List
from datetime import datetime

def collect_code(start_path: str, output_file: str) -> None:
    """Собирает весь код проекта и его зависимости в один файл"""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Записываем только критические метаданные
        project_info = {
            'name': 'FateAndLifeBot',
            'version': _get_version(start_path),
            'python_version': '3.13.2',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'main_modules': _get_modules(start_path),
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
        
        # Рекурсивно записываем все исходные файлы проекта
        all_files = _get_all_files(start_path)
        for file in all_files:
            if file.endswith('.py') or file in ['main_menu.py', 'inline_buttons.py']:  # ✅ Добавляем дополнительные файлы
                outfile.write(f"\n{'='*80}\n")
                outfile.write(f"# File: {file}\n")
                outfile.write(f"{'='*80}\n\n")
                outfile.write(_read_file(file))
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

def _get_modules(path: str) -> List[str]:
    """Получаем список всех модулей проекта"""
    modules = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.py') or file in ['main_menu.py', 'inline_buttons.py']:  # ✅ Добавляем нужные файлы
                modules.append(os.path.relpath(os.path.join(root, file), path))
    return modules

def _get_dependencies(path: str) -> List[str]:
    """Получаем зависимости проекта из requirements.txt (если существует)"""
    requirements_file = os.path.join(path, 'requirements.txt')
    if os.path.exists(requirements_file):
        return _read_file(requirements_file).splitlines()
    return []  # Если файл не найден, возвращаем пустой список

def _get_all_files(path: str) -> List[str]:
    """Получаем все файлы проекта, включая Python и другие файлы"""
    files = []
    for root, dirs, files_in_dir in os.walk(path):
        for file in files_in_dir:
            files.append(os.path.join(root, file))
    return files

def _read_file(path: str) -> str:
    """Безопасное чтение файла"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"# Error reading file: {str(e)}\n"

if __name__ == "__main__":
    project_root = "."  # Путь к корневой директории вашего проекта
    output_file = "full_project_code.txt"  # Файл для сохранения всего кода
    collect_code(project_root, output_file)
    print(f"Core code collection complete. Check {output_file}")
