import os
import yaml
from typing import List
from datetime import datetime

def collect_code(start_path: str, output_file: str) -> None:
    """Собирает весь код проекта и его зависимости в один файл."""
    project_root = os.path.abspath(start_path)
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Записываем метаданные проекта
            project_info = {
                'name': 'FateAndLifeBot',
                'version': _get_version(project_root),
                'python_version': '3.13.2',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'main_modules': _get_modules(project_root),
                'dependencies': _get_dependencies(project_root)
            }

            outfile.write("# Project Metadata:\n'''\n")
            yaml.dump(project_info, outfile, allow_unicode=True)
            outfile.write("'''\n\n")

            # Записываем конфигурационные файлы
            core_configs = _get_config_files(project_root)
            if core_configs:
                outfile.write("# Core Configuration Files:\n'''\n")
                yaml.dump(core_configs, outfile, allow_unicode=True)
                outfile.write("'''\n\n")

            # Записываем код всех файлов
            all_files = _get_all_files(project_root)
            for file in sorted(all_files):
                if file.endswith(('.py', '.json', '.yaml')) and not file.startswith('__pycache__'):
                    outfile.write(f"\n{'='*80}\n")
                    outfile.write(f"# File: {file}\n")
                    outfile.write(f"{'='*80}\n\n")
                    file_content = _read_file(os.path.join(project_root, file))
                    if file_content.strip():
                        outfile.write(file_content)
                        outfile.write("\n\n")

            # Записываем зависимости
            requirements_file = os.path.join(project_root, 'requirements.txt')
            if os.path.exists(requirements_file):
                outfile.write("# Dependencies (from requirements.txt):\n'''\n")
                outfile.write(_read_file(requirements_file))
                outfile.write("'''\n\n")

        print(f"✅ Сборка кода завершена. Проверьте {output_file}")
    except IOError as e:
        print(f"Ошибка при записи в файл {output_file}: {e}")
        raise

def _get_version(path: str) -> str:
    """Получает версию проекта из __init__.py."""
    try:
        for root, _, files in os.walk(path):
            if '__init__.py' in files:
                init_path = os.path.join(root, '__init__.py')
                with open(init_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('__version__'):
                            return line.split('=')[1].strip().strip("'").strip('"')
        return "0.1.0"
    except Exception as e:
        print(f"⚠️ Ошибка получения версии: {e}")
        return "0.1.0"

def _get_modules(path: str) -> List[str]:
    """Получает список всех модулей проекта."""
    modules = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for file in files:
            if file.endswith('.py') and not file.endswith('.pyc'):
                rel_path = os.path.relpath(os.path.join(root, file), path).replace("\\", "/")
                modules.append(rel_path)
    return modules

def _get_dependencies(path: str) -> List[str]:
    """Получает зависимости из requirements.txt."""
    requirements_file = os.path.join(path, 'requirements.txt')
    if os.path.exists(requirements_file):
        return _read_file(requirements_file).splitlines()
    return []

def _get_config_files(path: str) -> dict:
    """Получает содержимое конфигурационных файлов."""
    config_files = {}
    for file in ['.env']:
        file_path = os.path.join(path, file)
        if os.path.exists(file_path):
            config_files[file] = _read_file(file_path)
    return config_files

def _read_file(file_path: str) -> str:
    """Читает содержимое файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Ошибка чтения файла {file_path}: {e}")
        return ""

def _get_all_files(path: str) -> List[str]:
    """Получает список всех файлов в проекте, исключая __pycache__."""
    files = []
    for root, dirs, files_in_dir in os.walk(path):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for file in files_in_dir:
            if not file.endswith('.pyc'):
                rel_path = os.path.relpath(os.path.join(root, file), path).replace("\\", "/")
                files.append(rel_path)
    return files

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.dirname(__file__))
    collect_code(project_root, "full_project_code.txt")