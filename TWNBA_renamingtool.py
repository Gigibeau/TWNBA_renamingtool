import os
import glob
from tkinter import *  # NOQA
from tkinter import filedialog
import pandas as pd

root = Tk()

# Parameters
global current_directory
global lines_list
var_h = IntVar(value=1)
var_i = IntVar(value=1)
var_csv = IntVar(value=0)


def some_callback(event):
    # to delete the preset text once clicked
    event.widget.delete(0, "end")
    return None


button_open = Button(root, text="open", command=lambda: open_files())
button_open.grid(row=0, column=0)

checkbutton_h = Checkbutton(root, text='delete H-files', variable=var_h)
checkbutton_h.grid(row=0, column=1)
checkbutton_i = Checkbutton(root, text='delete I-files', variable=var_i)
checkbutton_i.grid(row=0, column=2)
checkbutton_csv = Checkbutton(root, text='rename summary.csv', variable=var_csv)
checkbutton_csv.grid(row=0, column=3)

entry_underscores = Entry(root, width=20)
entry_underscores.insert(END, 'How many underscores?')
entry_underscores.grid(row=0, column=4, columnspan=2)
entry_underscores.bind("<Button-1>", some_callback)

entry_lines = Entry(root, width=20)
entry_lines.insert(END, 'How many diffrent names?')
entry_lines.grid(row=1, column=0, columnspan=2)
entry_lines.bind("<Button-1>", some_callback)

button_lines = Button(root, text='Generate', command=lambda: generate_lines(int(entry_lines.get())))
button_lines.grid(row=1, column=2)

button_rename = Button(root, text='Rename', command=lambda: rename(var_h.get(), var_i.get(), var_csv.get(),
                                                                   entry_underscores.get()))
button_rename.grid(row=1, column=3)


def open_files():
    global current_directory
    current_directory = filedialog.askdirectory()


class Entryline:
    def __init__(self, row, old_name):
        self.lext_name = Entry(root, width=20)
        self.lext_name.insert(END, old_name)
        self.lext_name.grid(row=row, column=0, columnspan=2)
        self.lext_name.bind("<Button-1>", some_callback)

        self.new_name = Entry(root, width=20)
        self.new_name.insert(END, 'new name')
        self.new_name.grid(row=row, column=2, columnspan=2)
        self.new_name.bind("<Button-1>", some_callback)


def generate_lines(lines_count):
    global lines_list
    try:
        for count in range(len(lines_list)):
            try:
                lines_list[count].lext_name.grid_forget()
                lines_list[count].new_name.grid_forget()
            except (NameError, IndexError):
                pass
    except NameError:
        pass

    lines_list = []
    for line in range(lines_count):
        if line < 9:
            old_name = '000' + str(line + 1)
        else:
            old_name = '00' + str(line + 1)
        lines_list.append(Entryline(line + 2, old_name))


def rename(h_check, i_check, csv_check, underscores):
    # Loading the files in the same dictionary as the script
    files = glob.glob(current_directory + '/*')

    if underscores == 'How many underscores?':
        underscore_count = 2
    else:
        underscore_count = int(underscores)

    names = {}
    for line in range(len(lines_list)):
        if line < 9:
            old_name = '000' + str(line + 1)
        else:
            old_name = '00' + str(line + 1)

        names[old_name] = lines_list[line].new_name.get()

    # Looping through the files
    for file in files:
        file_sep = file.replace(".", "_")  # Replacing the '.' with a '_' to split the filetype aswell
        parts = file_sep.split('_')  # Splitting the old name in parts seperated by '_'

        if h_check:
            if parts[-2] == "H":
                os.remove(file)

        if i_check:
            if parts[-2] == "I":
                os.remove(file)

        # replacing the old names with the new names
        for key, value in names.items():
            if key == parts[underscore_count + 2]:
                # Renaming the 3D files
                if parts[-2] == "3D":
                    new_name_builder = ''
                    for underscore in range(underscore_count + 1):
                        new_name_builder += str(parts[underscore] + '_')

                    new_name = new_name_builder + value + '_3D' + "." + parts[-1]
                    print("Replacing " + file + "'s name with " + new_name)
                    os.rename(file, new_name)
                # Renaming the 2D files
                elif parts[-2] == "C":
                    new_name_builder = ''
                    for underscore in range(underscore_count + 1):
                        new_name_builder += str(parts[underscore] + '_')

                    new_name = new_name_builder + value + '_2D' + "." + parts[-1]
                    print("Replacing " + file + "'s name with " + new_name)
                    os.rename(file, new_name)
                    # Renaming all the other files
                else:
                    try:
                        new_name_builder = ''
                        for underscore in range(underscore_count + 1):
                            new_name_builder += str(parts[underscore] + '_')

                        new_name = new_name_builder + value + "." + parts[-1]
                        print("Replacing " + file + "'s name with " + new_name)
                        os.rename(file, new_name)
                    except FileNotFoundError:
                        pass

    if csv_check:
        csv_data = pd.read_csv(current_directory + '/summary.csv')
        csv_data = csv_data.rename(columns={"Dateiname": "LEXT name"})
        filenames = []

        for old_name in csv_data['LEXT name']:
            parts = old_name.split('_')

            # replacing the old names with the new names
            for key, value in names.items():
                if len(parts) < 4:
                    break

                if key == parts[underscore_count + 2]:
                    new_name_builder = ''
                    for underscore in range(underscore_count + 1):
                        new_name_builder += str(parts[underscore] + '_')

                    new_name = new_name_builder + value
                    print("Replacing " + old_name + "'s name with " + new_name)
                    filenames.append(new_name)

        csv_data['File name'] = pd.Series(filenames)
        csv_data.to_csv(current_directory + '/summary_final.csv', index=False)


root.mainloop()
