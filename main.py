
from fakturowania import setup_invoice, Menu

def main():
    menu = Menu()
    menu.add_choice("stockx invoice", setup_invoice)
    menu.display()

if __name__ == '__main__':
    main()
    
