import os
import tkinter as tk
from tkinter import filedialog, messagebox
from jira import JIRA
from P4 import P4, P4Exception
import time
import threading

# Variables globales pour les connexions
p4 = None
jira = None
perforce_connected = False
jira_connected = False
perforce_folders = []
jira_task = None

# Fonction de connexion à Perforce et Jira
def connecter():
    global p4, jira, perforce_connected, jira_connected

    # Connexion à Perforce
    p4 = P4()
    p4.user = perforce_user_entry.get()
    p4.password = perforce_password_entry.get()
    p4.port = perforce_server_entry.get()

    try:
        p4.connect()
        p4.run_login()
        perforce_connected = True
        messagebox.showinfo("Connexion Perforce", "Connexion à Perforce réussie !")
    except P4Exception as e:
        messagebox.showerror("Erreur Perforce", f"Erreur de connexion à Perforce : {e}")
        return

    # Connexion à Jira
    jira_url = jira_url_entry.get()
    jira_user = jira_user_entry.get()
    jira_token = jira_token_entry.get()

    try:
        jira = JIRA(server=jira_url, basic_auth=(jira_user, jira_token))
        jira_connected = True
        messagebox.showinfo("Connexion Jira", "Connexion à Jira réussie !")
    except Exception as e:
        messagebox.showerror("Erreur Jira", f"Erreur de connexion à Jira : {e}")
        return

# Fonction pour sélectionner plusieurs dossiers ou fichiers Perforce
def choisir_dossiers_perforce():
    if not perforce_connected:
        messagebox.showerror("Erreur", "Veuillez vous connecter à Perforce avant de continuer.")
        return

    folders = filedialog.askdirectory()
    if folders:
        perforce_folders.append(folders)
        dossier_perforce_label.config(text='\n'.join(perforce_folders))

# Fonction pour choisir une tâche Jira existante
def choisir_tache_jira():
    if not jira_connected:
        messagebox.showerror("Erreur", "Veuillez vous connecter à Jira avant de continuer.")
        return

    task_id = task_entry.get()
    try:
        issue = jira.issue(task_id)
        tache_jira_label.config(text=f"Tâche sélectionnée : {issue.key}")
        global jira_task
        jira_task = issue
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de trouver la tâche : {e}")

# Fonction pour surveiller les changements dans les dossiers Perforce
def surveiller_dossier():
    if not perforce_connected:
        messagebox.showerror("Erreur", "Veuillez vous connecter à Perforce avant de continuer.")
        return

    try:
        for folder in perforce_folders:
            changes = p4.run("changes", f"//depot/{os.path.basename(folder)}/...")
            if changes:
                messagebox.showinfo("Alerte", f"Des modifications ont été détectées dans {folder}")
                commentaire = f"Modification détectée dans Perforce : {changes[0]['change']}"
                jira.add_comment(jira_task, commentaire)
                messagebox.showinfo("Jira", f"Commentaire ajouté à la tâche {jira_task.key}")
            else:
                messagebox.showinfo("Info", f"Aucune modification détectée dans {folder}.")
    except P4Exception as e:
        messagebox.showerror("Erreur Perforce", f"Erreur : {e}")

# Fonction pour surveiller les changements dans la tâche Jira
def surveiller_tache_jira():
    global jira_task
    if not jira_task:
        messagebox.showerror("Erreur", "Veuillez sélectionner une tâche Jira avant de continuer.")
        return

    try:
        issue = jira.issue(jira_task.key)
        if issue.fields.status.name != jira_task.fields.status.name:
            messagebox.showinfo("Alerte Jira", f"Le statut de la tâche {jira_task.key} a changé : {issue.fields.status.name}")
            jira_task = issue
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la surveillance de la tâche Jira : {e}")

# Fonction de surveillance continue
def surveillance_continue():
    while True:
        surveiller_dossier()
        surveiller_tache_jira()
        time.sleep(300)  # Attendre 5 minutes

# Fonction pour démarrer la surveillance dans un thread séparé
def lancer_surveillance():
    if not perforce_connected or not jira_connected:
        messagebox.showerror("Erreur", "Veuillez vous connecter à Perforce et Jira avant de lancer la surveillance.")
        return

    thread = threading.Thread(target=surveillance_continue)
    thread.daemon = True
    thread.start()

# Fonction pour arrondir les coins des widgets Tkinter
def style_widgets(widget, bg_color="#333333", fg_color="white"):
    widget.config(bg=bg_color, fg=fg_color, bd=0, relief=tk.FLAT)
    widget.config(highlightbackground=bg_color, highlightthickness=0)

# Interface graphique avec Tkinter
root = tk.Tk()
root.title("Connexion et Surveillance Perforce/Jira")
root.geometry("400x600")
root.configure(bg="#2C2C2C")  # Couleur de fond : gris très sombre

# Styles généraux
bg_color = "#2C2C2C"  # Gris très sombre
fg_color = "white"  # Texte en blanc
entry_bg_color = "#3A3A3A"  # Arrière-plan des champs d'entrée en gris foncé
btn_bg_color = "#444444"  # Arrière-plan des boutons

# Connexion à Perforce
tk.Label(root, text="Perforce - Serveur :", bg=bg_color, fg=fg_color).pack(pady=5)
perforce_server_entry = tk.Entry(root, bg=entry_bg_color, fg=fg_color, insertbackground=fg_color, relief="groove")
perforce_server_entry.pack(pady=5)

tk.Label(root, text="Perforce - Nom d'utilisateur :", bg=bg_color, fg=fg_color).pack(pady=5)
perforce_user_entry = tk.Entry(root, bg=entry_bg_color, fg=fg_color, insertbackground=fg_color, relief="groove")
perforce_user_entry.pack(pady=5)

tk.Label(root, text="Perforce - Mot de passe :", bg=bg_color, fg=fg_color).pack(pady=5)
perforce_password_entry = tk.Entry(root, show='*', bg=entry_bg_color, fg=fg_color, insertbackground=fg_color, relief="groove")
perforce_password_entry.pack(pady=5)

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

# Bouton de connexion
connect_button = tk.Button(root, text="Connexion", command=connecter, bg=btn_bg_color, fg=fg_color, relief="groove", padx=10, pady=5)
connect_button.pack(pady=10)

# Sélectionner le dossier Perforce
tk.Label(root, text="Sélectionner les dossiers à surveiller :", bg=bg_color, fg=fg_color).pack(pady=5)
select_button = tk.Button(root, text="Choisir les dossiers", command=choisir_dossiers_perforce, bg=btn_bg_color, fg=fg_color, relief="groove", padx=10, pady=5)
select_button.pack(pady=10)

dossier_perforce_label = tk.Label(root, text="", bg=bg_color, fg=fg_color)
dossier_perforce_label.pack()

# Entrer la tâche Jira
tk.Label(root, text="Entrer l'ID de la tâche Jira :", bg=bg_color, fg=fg_color).pack(pady=5)
task_entry = tk.Entry(root, bg=entry_bg_color, fg=fg_color, insertbackground=fg_color, relief="groove")
task_entry.pack(pady=5)

select_task_button = tk.Button(root, text="Choisir la tâche", command=choisir_tache_jira, bg=btn_bg_color, fg=fg_color, relief="groove", padx=10, pady=5)
select_task_button.pack(pady=10)

tache_jira_label = tk.Label(root, text="", bg=bg_color, fg=fg_color)
tache_jira_label.pack()

# Bouton pour démarrer la surveillance continue
start_button = tk.Button(root, text="Démarrer la surveillance continue", command=lancer_surveillance, bg=btn_bg_color, fg=fg_color, relief="groove", padx=10, pady=5)
start_button.pack(pady=20)

root.mainloop()
