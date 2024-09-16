import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from jira import JIRA

# Variables globales
jira = None
project_key = None
branch_name = None

# Fonction pour se connecter à Jira
def connecter():
    global jira, project_key

    jira_url = jira_url_entry.get()
    jira_user = jira_user_entry.get()
    jira_token = jira_token_entry.get()

    try:
        jira = JIRA(server=jira_url, basic_auth=(jira_user, jira_token))
        project_key = project_entry.get().upper()
        messagebox.showinfo("Connexion Jira", "Connexion à Jira réussie !")
    except Exception as e:
        messagebox.showerror("Erreur Jira", f"Erreur de connexion à Jira : {e}")

# Fonction pour choisir le fichier Excel
def choisir_fichier():
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers Excel", "*.xlsx")])
    if file_path:
        file_label.config(text=f"Fichier sélectionné : {file_path}")
        global excel_file_path
        excel_file_path = file_path

# Fonction pour créer des tâches Jira depuis le fichier Excel
def creer_taches_jira():
    global jira, project_key, branch_name
    
    if not jira:
        messagebox.showerror("Erreur", "Veuillez vous connecter à Jira avant de continuer.")
        return

    if not excel_file_path:
        messagebox.showerror("Erreur", "Veuillez sélectionner un fichier Excel avant de continuer.")
        return
    
    branch_name = branch_entry.get()
    
    try:
        df = pd.read_excel(excel_file_path, header=None)
        
        for _, row in df.iterrows():
            main_task = row[0]
            sub_task = row[1]
            sub_sub_task = row[2]
            
            # Créer la tâche principale
            if pd.notna(main_task):
                main_issue = jira.create_issue(project=project_key, summary=main_task, description=f"Branche: {branch_name}", issuetype={'name': 'Task'})
                messagebox.showinfo("Création", f"Tâche principale créée : {main_issue.key}")
            
            # Créer la sous-tâche
            if pd.notna(sub_task):
                sub_issue = jira.create_issue(project=project_key, summary=sub_task, description=f"Branche: {branch_name}", issuetype={'name': 'Sub-task'}, parent={'key': main_issue.key})
                messagebox.showinfo("Création", f"Sous-tâche créée : {sub_issue.key}")
                
            # Créer la sous-sous-tâche
            if pd.notna(sub_sub_task):
                sub_sub_issue = jira.create_issue(project=project_key, summary=sub_sub_task, description=f"Branche: {branch_name}", issuetype={'name': 'Sub-task'}, parent={'key': sub_issue.key})
                messagebox.showinfo("Création", f"Sous-sous-tâche créée : {sub_sub_issue.key}")
    
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création des tâches : {e}")

# Interface graphique avec Tkinter
root = tk.Tk()
root.title("Création de Tâches Jira depuis Excel")
root.geometry("400x600")
root.configure(bg="#2C2C2C")

# Styles généraux
bg_color = "#2C2C2C"
fg_color = "white"
entry_bg_color = "#3A3A3A"
btn_bg_color = "#444444"

# Connexion à Jira
tk.Label(root, text="Jira - URL :", bg=bg_color, fg=fg_color).pack(pady=5)
jira_url_entry = tk.Entry(root, bg=entry_bg_color, fg=fg_color, insertbackground=fg_color, relief="groove")
jira_url_entry.pack(pady=5)

tk.Label(root, text="Jira - Nom d'utilisateur :", bg=bg_color, fg=fg_color).pack(pady=5)
jira_user_entry = tk.Entry(root, bg=entry_bg_color, fg=fg_color, insertbackground=fg_color, relief="groove")
jira_user_entry.pack(pady=5)

tk.Label(root, text="Jira - Token d'API :", bg=bg_color, fg=fg_color).pack(pady=5)
jira_token_entry = tk.Entry(root, show='*', bg=entry_bg_color, fg=fg_color, insertbackground=fg_color, relief="groove")
jira_token_entry.pack(pady=5)

tk.Label(root, text="Projet Jira (Key) :", bg=bg_color, fg=fg_color).pack(pady=5)
project_entry = tk.Entry(root, bg=entry_bg_color, fg=fg_color, insertbackground=fg_color, relief="groove")
project_entry.pack(pady=5)

tk.Label(root, text="Nom de la branche :", bg=bg_color, fg=fg_color).pack(pady=5)
branch_entry = tk.Entry(root, bg=entry_bg_color, fg=fg_color, insertbackground=fg_color, relief="groove")
branch_entry.pack(pady=5)

connect_button = tk.Button(root, text="Connexion Jira", command=connecter, bg=btn_bg_color, fg=fg_color, relief="groove", padx=10, pady=5)
connect_button.pack(pady=10)

# Sélection du fichier Excel
tk.Button(root, text="Choisir le fichier Excel", command=choisir_fichier, bg=btn_bg_color, fg=fg_color, relief="groove", padx=10, pady=5).pack(pady=10)
file_label = tk.Label(root, text="", bg=bg_color, fg=fg_color)
file_label.pack(pady=5)

# Créer les tâches Jira depuis le fichier Excel
tk.Button(root, text="Créer les tâches Jira", command=creer_taches_jira, bg=btn_bg_color, fg=fg_color, relief="groove", padx=10, pady=5).pack(pady=20)

root.mainloop()
