import os
import csv
from operator import itemgetter


class PriceMachine:
    def __init__(self):
        self.data = []

    def load_prices(self, directory):
        for file in os.listdir(directory):
            if 'price' in file.lower() and file.endswith('.csv'):
                self._process_file(os.path.join(directory, file))

    def _process_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=',')
            product_column = self._find_column_name(reader.fieldnames, ['название', 'продукт', 'товар', 'наименование'])
            price_column = self._find_column_name(reader.fieldnames, ['цена', 'розница'])
            weight_column = self._find_column_name(reader.fieldnames, ['фасовка', 'масса', 'вес'])

            if not product_column or not price_column or not weight_column:
                print(f"В файле '{filepath}' не найдены все необходимые столбцы.")
                return

            for row in reader:
                try:
                    price = float(row[price_column])
                    weight = float(row[weight_column])
                    price_per_kg = price / weight
                    self.data.append({
                        'product': row[product_column],
                        'price': price,
                        'weight': weight,
                        'file': os.path.basename(filepath),
                        'price_per_kg': price_per_kg
                    })
                except (ValueError, ZeroDivisionError) as e:
                    print(f"Ошибка обработки данных в файле {filepath}: {e}")
                    continue

    def _find_column_name(self, headers, options):
        for header in headers:
            if any(opt in header.lower() for opt in options):
                return header
        return None

    def find_text(self, text):
        matches = [item for item in self.data if text.lower() in item['product'].lower()]
        return sorted(matches, key=itemgetter('price_per_kg'))

    def export_to_html(self, filename='prices.html'):
        sorted_data = sorted(self.data, key=itemgetter('price_per_kg'))

        with open(filename, 'w', encoding='utf-8') as file:
            file.write('<html><head><meta charset="UTF-8"><title>Price List</title></head><body><table border="1">\n')
            file.write(
                '<tr><th>№</th><th>Наименование</th><th>Цена</th><th>Вес</th><th>Файл</th><th>Цена за кг.</th></tr>\n')
            for index, item in enumerate(sorted_data, 1):
                file.write(
                    f'<tr><td>{index}</td><td>{item["product"]}</td><td>{item["price"]}</td><td>{item["weight"]}</td>'
                    f'<td>{item["file"]}</td><td>{item["price_per_kg"]:.2f}</td></tr>\n')
            file.write('</table></body></html>')


def main():
    analyzer = PriceMachine()
    directory = '.'
    analyzer.load_prices(directory)

    while True:
        query = input('Введите название товара для поиска или "exit" для выхода: ')
        if query.lower() == 'exit':
            print("Работа завершена.")
            break

        results = analyzer.find_text(query)
        if results:
            print("{:<4} {:<40} {:<10} {:<8} {:<15} {:<12}".format("№", "Наименование", "Цена", "Вес", "Файл",
                                                                   "Цена за кг."))
            for i, result in enumerate(results, 1):
                print("{:<4} {:<40} {:<10} {:<8} {:<15} {:<12.2f}".format(
                    i, result['product'], result['price'], result['weight'], result['file'], result['price_per_kg']
                ))
        else:
            print("Совпадения не найдены.")

    exporter_choice = input('Хотите экспортировать данные в HTML? (да/нет): ')
    if exporter_choice.lower() == 'да':
        analyzer.export_to_html()
        print("Данные экспортированы в 'prices.html'.")


if __name__ == '__main__':
    main()
