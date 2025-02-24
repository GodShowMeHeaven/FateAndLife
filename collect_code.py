import os
import yaml
from typing import List
from datetime import datetime

def collect_code(start_path: str, output_file: str) -> None:
    """Собирает весь код проекта и его зависимости в один файл"""

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Записываем метаданные проекта
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

        # Записываем все конфигурационные файлы (включаем .yaml, .json, .env)
        core_configs = _get_config_files(start_path)
        if core_configs:
            outfile.write("# Core Configuration Files:\n'''\n")
            yaml.dump(core_configs, outfile, allow_unicode=True)
            outfile.write("'''\n\n")

        # Рекурсивно записываем весь код и другие важные файлы
        all_files = _get_all_files(start_path)
        for file in sorted(all_files):  # Добавлена сортировка для читаемости
            if file.endswith('.py') or file.endswith('.json') or file.endswith('.yaml'):
                outfile.write(f"\n{'='*80}\n")
                outfile.write(f"# File: {file}\n")
                outfile.write(f"{'='*80}\n\n")
                file_content = _read_file(file)
                if file_content.strip():  # Пропускаем пустые файлы
                    outfile.write(file_content)
                    outfile.write("\n\n")

        # Записываем зависимости
        requirements_file = os.path.join(start_path, 'requirements.txt')
        if os.path.exists(requirements_file):
            outfile.write("# Dependencies (from requirements.txt):\n'''\n")
            outfile.write(_read_file(requirements_file))
            outfile.write("'''\n\n")

    print(f"✅ Code collection complete. Check {output_file}")

def _get_version(path: str) -> str:
    """Получает версию проекта из __init__.py"""
    try:
        # Поиск файла __init__.py в папке проекта
        for root, dirs, files in os.walk(path):
            if '__init__.py' in files:
                init_path = os.path.join(root, '__init__.py')
                with open(init_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('__version__'):
                            return line.split('=')[1].strip().strip("'").strip('"')
        print("⚠️ Warning: __init__.py not found. Using default version 0.1.0")
        return "0.1.0"
    except Exception as e:
        print(f"⚠️ Error retrieving version: {e}")
        return "0.1.0"

def _get_modules(path: str) -> List[str]:
    """Получает список всех модулей проекта"""
    modules = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                rel_path = os.path.relpath(os.path.join(root, file), path)
                modules.append(rel_path.replace("\\", "/"))  # Для кроссплатформенности
    return modules

def _get_dependencies(path: str) -> List[str]:
    """Получает зависимости из requirements.txt (если он существует)"""
    requirements_file = os.path.join(path, 'requirements.txt')
    if os.path.exists(requirements_file):
        deps = _read_file(requirements_file).splitlines()
        return [dep for dep in deps if dep.strip()]  # Убираем пустые строки
    return ["⚠️ No dependencies found"]

def _get_config_files(path: str) -> dict:
    """Собирает содержимое всех конфигурационных файлов (.yaml, .json, .env)"""
    config_files = {}
    for ext in ['.yaml', '.json', '.env']:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(ext):
                    full_path = os.path.join(root, file)
                    config_files[file] = _read_file(full_path)
    return config_files

def _get_all_files(path: str) -> List[str]:
    """Получает все файлы проекта, включая код и конфигурационные файлы"""
    files = []
    for root, dirs, files_in_dir in os.walk(path):
        for file in files_in_dir:
            rel_path = os.path.relpath(os.path.join(root, file), path)
            files.append(rel_path.replace("\\", "/"))  # Для кроссплатформенности
    return files

def _read_file(path: str) -> str:
    """Безопасное чтение файла"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"# Error reading file: {str(e)}\n"

if __name__ == "__main__":
    project_root = "."  # Путь к корневой директории проекта
    output_file = "full_project_code.txt"
    collect_code(project_root, output_file)
