import sys
import os
from datetime import datetime


if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def read_log_file(filepath):
    """Читає вміст файлу логу. Повертає назву гілки та список рядків логу."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Помилка: Файл за шляхом '{filepath}' не знайдено.")
    

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        lines = [line.strip() for line in file if line.strip()]
        
    if not lines:
        raise ValueError("Помилка: Файл логу порожній.")
        
    branch_name = lines[0]
    log_lines = lines[1:]
    
    return branch_name, log_lines

def parse_commit_line(line):
    """Парсить один рядок логу за форматом: хеш|автор|дата|повідомлення."""
    parts = line.split('|')
    if len(parts) < 4:
        raise ValueError(f"Неправильний формат рядка коміту: {line}")
        
    commit_hash = parts[0]
    author = parts[1]
    date_str = parts[2]
    message = "|".join(parts[3:]) if parts[3:] else "Без повідомлення"
    
    try:
        commit_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            commit_date = datetime.fromisoformat(date_str.split()[0])
        except Exception:
            commit_date = datetime.min
            
    return {
        "hash": commit_hash,
        "author": author,
        "date": commit_date,
        "message": message,
        "original_date_str": date_str     }

def analyze_branch_data(log_lines):
    """Аналізує список комітів і будує статистику."""
    commits = []
    authors = set()
    
    for line in log_lines:
        try:
            commit_data = parse_commit_line(line)
            commits.append(commit_data)
            authors.add(commit_data["author"])
        except ValueError as e:
            print(f"[Попередження] Пропущено пошкоджений рядок: {e}")
            continue

    if not commits:
        return None

    commits.sort(key=lambda x: x["date"])
    
    return {
        "total_commits": len(commits),
        "total_authors": len(authors),
        "first_commit": commits[0],
        "last_commit": commits[-1]
    }

def print_formatted_report(branch_name, stats):
    """Виводить фінальний форматований звіт у консоль."""
    if not stats:
        print(f"=== Звіт по гілці: {branch_name} ===")
        print("Немає даних для відображення комітів.\n")
        return

    first = stats["first_commit"]
    last = stats["last_commit"]

    print(f"=== Звіт по гілці: {branch_name} ===\n")
    print(f"Комітів: {stats['total_commits']}")
    print(f"Авторів: {stats['total_authors']}")
    print(f"Перший коміт: {first['original_date_str']} — \"{first['message']}\"")
    print(f"Останній коміт: {last['original_date_str']} — \"{last['message']}\"")
    print("\n" + "="*30 + "\n")

def main():
    """Головна функція керування скриптом."""
    if len(sys.argv) < 2:
        print("Помилка: Не вказано файл логу.")
        print("Використання: python analyzer.py <шлях_до_файлу_логу>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    
    try:
        branch_name, log_lines = read_log_file(filepath)
        stats = analyze_branch_data(log_lines)
        print_formatted_report(branch_name, stats)
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Помилка виконання: {e}")
    except Exception as e:
        print(f"Непередбачувана помилка під час аналізу: {e}")

if __name__ == "__main__":
    main()
