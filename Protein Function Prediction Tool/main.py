from Tkinter import *
import tkFileDialog
from recommendations import *


class GO_term():
    def __init__(self, id, name):
        self.id = id
        self.name = name
class evidence_code():
    def __init__(self, code, value):
        self.code = code
        self.value = value
class annotation():
    def __init__(self, GO, evidence):
        self.GO = GO
        self.evidence = evidence
class protein():
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.annotations = {}
class data_center():
    def __init__(self):
        self.proteins = {}
        self.all_ready = [] # This list is populated as the required files loaded successfully.
    def open_annotation(self):
        filename = tkFileDialog.askopenfilename(initialdir="/", title="Select Annotation File", filetypes=(("Annotation File", "*.gaf"), ("all files", "*.*")))
        if filename.split(".")[1] != "gaf":
            raise Exception
        new_file = open(filename,'r')
        lines = new_file.readlines()
        self.geo_human_dict = {} # Data from the annotations file is stored in here for the later use.
        for i in lines:
            if i[0] == "!":
                continue
            line_data = i.split("\t")
            protein_id = line_data[1]
            protein_name = line_data[2]
            protein_go = line_data[4]
            protein_evidence = line_data[6]
            if protein_id not in self.geo_human_dict:
                self.geo_human_dict[protein_id] = {"id":protein_id, "name":protein_name, "annotations":{protein_go:protein_evidence}}
            else:
                self.geo_human_dict[protein_id]["annotations"][protein_go] = protein_evidence
        new_file.close()
    def open_evidence(self): # Opens the evidence file and stores the evidence objects.
        filename = tkFileDialog.askopenfilename(initialdir="/", title="Select ECV File", filetypes=(("ECV File", "*.txt"), ("all files", "*.*")))
        new_file = open(filename, 'r')
        lines = new_file.readlines()
        self.evidence_objects = {}
        for i in lines:
            line_data = i.strip('\n').split('\t')
            self.evidence_objects[line_data[0]] = evidence_code(line_data[0], float(line_data[1]))
        new_file.close()
    def open_go(self):  # Opens the go file and stores the go objects.
        filename = tkFileDialog.askopenfilename(initialdir="/", title="Select GO File", filetypes=(("GO File", "*.obo"), ("all files", "*.*")))
        if filename.split(".")[1] != "obo":
            raise Exception
        new_file = open(filename, 'r')
        lines = new_file.readlines()
        self.go_objects = {}
        for i in range(0, len(lines), 2):
            self.go_objects[lines[i][4:].strip('\n')] = GO_term(lines[i][4:].strip('\n'), lines[i+1][6:].strip('\n'))
        new_file.close()
    def finalize(self):
        if len(self.all_ready) == 3: # If all the files are loaded successfully, it starts to create the protein objects.
            for protein_id in self.geo_human_dict:
                protein_name = self.geo_human_dict[protein_id]["name"]
                self.proteins[protein_id] = protein(protein_id, protein_name)
                for protein_go in self.geo_human_dict[protein_id]["annotations"]:
                    protein_evidence = self.geo_human_dict[protein_id]["annotations"][protein_go]
                    self.proteins[protein_id].annotations[protein_go] = annotation(self.go_objects[protein_go], self.evidence_objects[protein_evidence])
            # Creating a protein dictionary similar to the critics in recommendations.py
            self.protein_dict = {}
            for i in self.proteins:
                self.protein_dict[self.proteins[i].id] = {}
                for j in self.proteins[i].annotations:
                    self.protein_dict[self.proteins[i].id][j] = self.proteins[i].annotations[j].evidence.value
            # Creating a dictionary of ProteinName:ProteinID pairs
            self.p_name_id = {}
            for i in self.proteins:
                p_name = self.proteins[i].name
                self.p_name_id[p_name] = i
class GUI(Frame):
    def __init__(self, master):
        self.master = master
        Frame.__init__(self, master)
        self.data = data_center()
        self.initUI(master)
    def initUI(self, master):
        self.color1 = "seashell4"
        self.color2 = "gray17"
        self.color3 = "seashell3"
        self.var = IntVar()
        self.var.set(1)
        self.frame1 = Frame(self) # Includes the 3 button on the top
        self.frame2 = Frame(self) # Includes the frames for similarity metric box and list boxes at the bottom.
        self.frame_proteins = Frame(self.frame2)
        self.frame_similarity = Frame(self.frame2)
        self.frame_similarity_inner = Frame(self.frame_similarity, highlightbackground=self.color2, highlightcolor=self.color2, highlightthickness=1)
        self.frame_sim_protein = Frame(self.frame2)
        self.frame_function = Frame(self.frame2)
        # Header and buttons
        self.label_header = Label(self, text="PROTEIN FUNCTION PREDICTION TOOL", font=("Century Gothic", 12), bg=self.color2, fg="white")
        self.label_header.pack(ipadx=60, ipady=5, pady=(0,20), fill=X)
        self.button_annotations = Button(self.frame1, text="Upload\nAnnotations", relief="groove", bg=self.color1, fg="white", command=self.open_annotation)
        self.button_annotations.pack(side=LEFT, ipadx=5, padx=10)
        self.button_evidence = Button(self.frame1, text="Upload Evidence\nCode Values", relief="groove", bg=self.color1, fg="white", command=self.open_evidence, disabledforeground="white")
        self.button_evidence.pack(side=LEFT, ipadx=5, padx=10)
        self.button_go = Button(self.frame1, text="Upload\nGO File", relief="groove", bg=self.color1, fg="white", command=self.open_go, disabledforeground="white")
        self.button_go.pack(side=LEFT, ipadx=5, padx=10)
        # Proteins
        self.label_proteins = Label(self.frame_proteins, text="Proteins", font=("", 9, "bold"))
        self.label_proteins.grid(row=0, column=0)
        self.scroll_proteins = Scrollbar(self.frame_proteins)
        self.scroll_proteins.grid(row=1, column=1, sticky=N+S)
        self.list_proteins = Listbox(self.frame_proteins, width=30, yscrollcommand=self.scroll_proteins.set, relief=FLAT, selectbackground=self.color1, highlightbackground=self.color2, highlightcolor=self.color2)
        self.list_proteins.grid(row=1, column=0, sticky=N+S)
        self.list_proteins.bind('<<ListboxSelect>>', self.show_similar)
        self.scroll_proteins.config(command=self.list_proteins.yview)
        # Similarity Metric
        self.label_similarity = Label(self.frame_similarity, text="Similarity Metric", font=("", 9, "bold"))
        self.label_similarity.grid(row=0, column=0)
        self.radio_pearson = Radiobutton(self.frame_similarity_inner, text="Pearson", variable=self.var, value=0, command=self.call_show_similar)
        self.radio_pearson.pack(pady=(10,0))
        self.radio_euclidean = Radiobutton(self.frame_similarity_inner, text="Euclidean", variable=self.var, value=1, command=self.call_show_similar)
        self.radio_euclidean.pack()
        # Similar Proteins
        self.label_sim_protein = Label(self.frame_sim_protein, text="Similar Proteins", font=("", 9, "bold"))
        self.label_sim_protein.grid(row=0, column=2)
        self.scroll_sim_protein = Scrollbar(self.frame_sim_protein)
        self.scroll_sim_protein.grid(row=1, column=3, sticky=N+S)
        self.list_sim_protein = Listbox(self.frame_sim_protein, width=45, relief=FLAT, yscrollcommand=self.scroll_sim_protein.set, highlightbackground=self.color2, selectbackground=self.color1, highlightcolor=self.color2)
        self.list_sim_protein.grid(row=1, column=2, sticky=N+S)
        self.scroll_sim_protein.config(command=self.list_sim_protein.yview)
        # Predicted Functions
        self.label_function = Label(self.frame_function, text="Predicted Functions", font=("", 9, "bold"))
        self.label_function.grid(row=0, column=2)
        self.scroll_function = Scrollbar(self.frame_function, highlightbackground=self.color1)
        self.scroll_function.grid(row=1, column=3, sticky=N+S)
        self.list_function = Listbox(self.frame_function, width=75, relief=FLAT, yscrollcommand=self.scroll_function.set, selectbackground=self.color1, highlightbackground=self.color2, highlightcolor=self.color2)
        self.list_function.grid(row=1, column=2, sticky=N+S)
        self.scroll_function.config(command=self.list_function.yview)
        # Pack, Grid, Row and Column Configure - List boxes can expand vertically with the window.
        self.frame_proteins.grid(row=0, column=0, padx=(0,25), sticky=N+S)
        self.frame_proteins.rowconfigure(1, weight=1)
        self.frame_similarity_inner.grid(row=1, column=0, sticky=(N+S+W+E), ipadx=10)
        self.frame_similarity.grid(row=0, column=1, padx=(0,25), sticky=N+S)
        self.frame_similarity.rowconfigure(1, weight=1)
        self.frame_similarity.columnconfigure(0, weight=1)
        self.frame_sim_protein.grid(row=0, column=2, padx=(0,25), sticky=N+S)
        self.frame_sim_protein.rowconfigure(1, weight=1)
        self.frame_function.grid(row=0, column=3, sticky=N+S)
        self.frame_function.rowconfigure(1, weight=1)
        self.frame1.pack(pady=(0,20))
        self.frame2.pack(pady=(0,30), padx=30, fill=Y, expand=True)
        self.frame2.rowconfigure(0, weight=1, minsize=230)
        self.pack(fill=BOTH, expand=True)
    def open_annotation(self): # These methods are calling the matching methods from the self.data object, and making sure they load the file without a problem.
        try:
            self.data.open_annotation()
            self.list_proteins.delete('0', END)
            for i in sorted(self.data.geo_human_dict):
                self.list_proteins.insert(END, self.data.geo_human_dict[i]["name"])
            self.button_annotations.configure(state=NORMAL, relief="groove", bg=self.color3)
            if "1" not in self.data.all_ready:
                self.data.all_ready.append("1")
            self.data.finalize()
        except Exception:
            pass
    def open_evidence(self):
        try:
            self.data.open_evidence()
            self.button_evidence.configure(state=NORMAL, relief="groove", bg=self.color3)
            if "2" not in self.data.all_ready:
                self.data.all_ready.append("2")
            self.data.finalize()
            self.show_similar("<<ListboxSelect>>") # In case an item from the protein listbox is already selected before loading the files.
        except Exception:
            pass
    def open_go(self):
        try:
            self.data.open_go()
            self.button_go.configure(state=NORMAL, relief="groove", bg=self.color3)
            if "3" not in self.data.all_ready:
                self.data.all_ready.append("3")
            self.data.finalize()
            self.show_similar("<<ListboxSelect>>") # In case an item from the protein listbox is already selected before loading the files.
        except Exception:
            pass
    def call_show_similar(self): # Radio buttons using this method as a command to reach the show_similar method.
        self.show_similar("<<ListboxSelect>>")
    def show_similar(self, event):
        try:
            self.list_sim_protein.delete("0", END)
            self.list_function.delete("0", END)
            similarity = sim_pearson
            if self.var.get() == 1:
                similarity = sim_distance
            if len(self.data.all_ready) == 3:
                selected = self.data.p_name_id[self.list_proteins.get(self.list_proteins.curselection())]
                matches = topMatches(self.data.protein_dict, selected, 1000, similarity)
                for i in matches:
                    if i[0]>0:
                        self.list_sim_protein.insert(END, str(round(i[0],1)) + " - " + i[1] + " - " + self.data.proteins[i[1]].name)
                predicted = getRecommendations(self.data.protein_dict, selected, similarity)
                for i in predicted:
                    self.list_function.insert(END, str(round(i[0],1))+" - "+i[1]+" - "+self.data.go_objects[i[1]].name)
        except Exception:
            pass
def main():
    root = Tk()
    root.title("Protein Function Prediction Tool")
    app = GUI(root)

    root.mainloop()
main()