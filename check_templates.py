import os

print("Проверка структуры проекта...")
print("=" * 60)

# Текущая папка
current_dir = os.getcwd()
print(f"Текущая папка: {current_dir}")

# Проверяем важные пути
paths_to_check = [
    'web/templates/index.html',
    'web/templates/flute_view.html',
    'web/__init__.py',
    'web/routes.py',
    'database/models.py',
    'core/calculator.py'
]

print("\nПроверка файлов:")
print("-" * 60)
for path in paths_to_check:
    full_path = os.path.join(current_dir, path)
    exists = os.path.exists(full_path)
    status = "✓ СУЩЕСТВУЕТ" if exists else "✗ ОТСУТСТВУЕТ"
    print(f"{status}: {path}")

# Проверяем структуру templates
print("\nСодержимое web/templates:")
print("-" * 60)
templates_dir = os.path.join(current_dir, 'web', 'templates')
if os.path.exists(templates_dir):
    for file in os.listdir(templates_dir):
        print(f"  • {file}")
else:
    print("  Папка templates не найдена!")

print("\n" + "=" * 60)
input("Нажмите Enter для продолжения...")