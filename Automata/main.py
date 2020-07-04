from Automata import Otomat
import json

def parse_input_file(filepath):
    '''
        Đọc otomat từ 1 file json và trả về otomat đó
        Args: 
            filepath: path to file that will be parsed
        Returns:
            Otomat
    '''
    with open(filepath, 'r') as f:
        data = json.load(f)
        f.close()
    fields = ["sigma", "S", "S0", "F", "delta"]
    for field in fields:
        if field not in data.keys():
            print(f"Thiếu thành phần {field}. Xin kiểm tra lại file đầu vào")
            exit(0)
    otomat = {key:data[key] for key in fields}
    return Otomat(**otomat)

def main():
    filepath = input('Nhập tên file đầu vào: ')
    otomat = parse_input_file(filepath)
    print("Otomat ban đầu")
    otomat.printOtomat()

    # Đơn định hóa
    # otomat.DFA()
    # print("Otomat sau khi đơn định hóa")
    # otomat.printOtomat()

    # Tối thiểu hóa
    otomat.minimize()
    print("Otomat sau khi tối thiểu hóa")
    otomat.printOtomat()

if __name__ == '__main__':
    main()