import os
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
import logging
from tkinter import filedialog, Tk, messagebox, Text, END
from datetime import datetime

#Tworzenie folderu log
log_folder = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_folder, exist_ok=True)

def setup_logger():
    #Każdy log zapisywany jest jako konkretna niepowtarzalna data
    log_file = os.path.join(log_folder, datetime.now().strftime("%Y-%m-%d_%H-%M-%S_errors.log"))
    logging.basicConfig(filename=log_file, level=logging.ERROR, format='%(asctime)s - %(message)s')

#funkcja konwertująca z json do xml
def json_to_xml(data, parent):
    for key, value in data.items():
        if isinstance(value, dict):
            element = ET.SubElement(parent, key)
            json_to_xml(value, element)
        else:
            element = ET.SubElement(parent, key)
            element.text = str(value)

#procesowanie kolejnych plików json
def process_json_files(json_folder, xml_folder):
    success_messages = []
    error_messages = []

    for filename in os.listdir(json_folder):
        try:
            json_filepath = os.path.join(json_folder, filename)

            if not filename.lower().endswith('.json'):
                continue

            with open(json_filepath, 'r') as json_file:
                json_data = json.load(json_file)

            xml_root = ET.Element('root')

            json_to_xml(json_data, xml_root)

            xml_tree = ET.ElementTree(xml_root)

            xml_filename = os.path.splitext(filename)[0] + '.xml'
            xml_filepath = os.path.join(xml_folder, xml_filename)

            xml_str = ET.tostring(xml_root, encoding='utf-8')
            xml_dom = xml.dom.minidom.parseString(xml_str)
            pretty_xml_str = xml_dom.toprettyxml(indent='  ')

            with open(xml_filepath, 'w') as xml_file:
                xml_file.write(pretty_xml_str)

            success_messages.append(f"Utworzono plik XML: {xml_filepath}")

            #Okno aplikacji informuje nas o przebiegu działania programu
            update_message_window(success_messages[-1])

        except Exception as e:
            error_msg = f"Błąd podczas przetwarzania pliku {filename}: {e}"
            logging.error(error_msg)
            error_messages.append(error_msg)

    if not success_messages and not error_messages:
        update_message_window("Nie znaleziono plików JSON w wybranym folderze.")

def update_message_window(message):
    root.update_idletasks()
    message_text.insert(END, message + "\n")

#Wyświetlenie okna z komunikatem o wybranie folderu z plikami JSON, które chcemy konwertować
json_folder = filedialog.askdirectory(title="Wybierz folder z plikami JSON")

#Jeśli kliniemy 'anuluj', program zakończy działanie i poinformuje o nie wybraniu folderu
if not json_folder:
    messagebox.showerror("Błąd", "Nie wybrano folderu, spróbuj ponownie.")
    exit()

#wybieramy folder docelowy zapisu
xml_folder = filedialog.askdirectory(title="Wybierz folder do zapisu plików XML")

#Jeśli kliniemy 'anuluj', program zakończy działanie i poinformuje o nie wybraniu folderu
if not xml_folder:
    messagebox.showerror("Błąd", "Anulowano wybór folderu do zapisu plików XML")
    exit()

setup_logger()

#Tworzymy okno Tkinter do wyświetlania wiadomości
root = Tk()
root.title("Komunikaty")

message_text = Text(root, height=10, wrap='word')
message_text.pack(pady=10)

#Wywołujemy konwersję plików
process_json_files(json_folder, xml_folder)

root.mainloop()
