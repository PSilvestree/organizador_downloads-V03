import threading
import time
import os
import shutil
from datetime import datetime
from collections import defaultdict
from PIL import Image, ImageDraw
import pystray
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# ============================================
# CONFIGURAÇÕES
# ============================================

PASTA_MONITORADA = os.path.expanduser("~/Downloads")
PASTA_DESTINO = os.path.expanduser("~/Organizador")

CATEGORIAS = {
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "PDFs": [".pdf"],
    "Documentos": [".doc", ".docx", ".txt", ".xlsx", ".xls", ".pptx", ".odt"],
    "Vídeos": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"],
    "Áudios": [".mp3", ".wav", ".flac", ".aac", ".m4a", ".wma"],
    "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
    "Executáveis": [".exe", ".msi", ".app", ".dmg", ".deb"],
    "Código": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".sql"],
}

# ============================================
# MONITOR
# ============================================

class OrganizadorArquivos(FileSystemEventHandler):
    def __init__(self, callback=None):
        self.callback = callback
        self.contador = defaultdict(int)
    
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)
            self.organizar_arquivo(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            time.sleep(0.5)
            try:
                if os.path.getsize(event.src_path) > 1024 * 1024:
                    self.organizar_arquivo(event.src_path)
            except:
                pass
    
    def organizar_arquivo(self, caminho_arquivo):
        try:
            nome_arquivo = os.path.basename(caminho_arquivo)
            if nome_arquivo.startswith(".") or nome_arquivo.endswith(".part"):
                return
            
            max_tentativas = 10
            for tentativa in range(max_tentativas):
                try:
                    with open(caminho_arquivo, 'rb'):
                        pass
                    break
                except:
                    if tentativa < max_tentativas - 1:
                        time.sleep(1)
                    else:
                        return
            
            _, extensao = os.path.splitext(nome_arquivo)
            extensao = extensao.lower()
            
            categoria = "Outros"
            for cat, extensoes in CATEGORIAS.items():
                if extensao in extensoes:
                    categoria = cat
                    break
            
            pasta_categoria = os.path.join(PASTA_DESTINO, categoria)
            os.makedirs(pasta_categoria, exist_ok=True)
            
            caminho_destino = os.path.join(pasta_categoria, nome_arquivo)
            
            contador = 1
            nome_base, ext = os.path.splitext(nome_arquivo)
            while os.path.exists(caminho_destino):
                novo_nome = f"{nome_base}_{contador}{ext}"
                caminho_destino = os.path.join(pasta_categoria, novo_nome)
                contador += 1
            
            shutil.move(caminho_arquivo, caminho_destino)
            self.contador[categoria] += 1
            
            if self.callback:
                self.callback(nome_arquivo, categoria)
            
            notification.notify(
                title="✅ Arquivo Organizado!",
                message=f"{nome_arquivo}\n📁 {categoria}",
                timeout=5,
                app_name="Organizador de Downloads"
            )
            
        except Exception as e:
            print(f"❌ Erro: {e}")

# ============================================
# THREAD DO MONITOR
# ============================================

class MonitorEmThread(threading.Thread):
    def __init__(self, callback=None):
        super().__init__(daemon=True)
        self.observer = None
        self.rodando = True
        self.handler = OrganizadorArquivos(callback)
    
    def run(self):
        self.observer = Observer()
        self.observer.schedule(self.handler, PASTA_MONITORADA, recursive=False)
        self.observer.start()
        
        try:
            while self.rodando and self.observer.is_alive():
                self.observer.join(timeout=1)
        except KeyboardInterrupt:
            self.parar()
    
    def parar(self):
        self.rodando = False
        if self.observer:
            self.observer.stop()
            self.observer.join()

# ============================================
# JANELA TKINTER
# ============================================

class JanelaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("📥 Organizador de Downloads")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        
        self.monitor_thread = None
        self.criar_ui()
        self.iniciar_monitor()
    
    def criar_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#2d2d2d")
        header.pack(fill=tk.X, padx=0, pady=0)
        
        tk.Label(header, text="📥 Organizador de Downloads",
                bg="#2d2d2d", fg="#42a5f5", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=15, pady=10)
        
        # Notebook (Abas)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba 1: Dashboard
        aba1 = tk.Frame(notebook, bg="#2d2d2d")
        notebook.add(aba1, text="📊 Dashboard")
        self.criar_dashboard(aba1)
        
        # Aba 2: Log
        aba2 = tk.Frame(notebook, bg="#2d2d2d")
        notebook.add(aba2, text="📋 Log")
        self.criar_log(aba2)
        
        # Aba 3: Config
        aba3 = tk.Frame(notebook, bg="#2d2d2d")
        notebook.add(aba3, text="⚙️ Config")
        self.criar_config(aba3)
        
        # Footer
        footer = tk.Frame(self.root, bg="#2d2d2d")
        footer.pack(fill=tk.X, padx=0, pady=0)
        
        tk.Button(footer, text="🔄 Atualizar", bg="#42a5f5", fg="white", relief=tk.FLAT,
                 command=self.atualizar).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(footer, text="📁 Abrir", bg="#42a5f5", fg="white", relief=tk.FLAT,
                 command=self.abrir_pasta).pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Label(footer, bg="#2d2d2d").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(footer, text="➖ Minimizar", bg="#666666", fg="white", relief=tk.FLAT,
                 command=lambda: self.root.withdraw()).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(footer, text="🛑 Sair", bg="#ff5252", fg="white", relief=tk.FLAT,
                 command=self.fechar).pack(side=tk.RIGHT, padx=5, pady=5)
    
    def criar_dashboard(self, parent):
        info_text = f"""📂 Monitorando: {PASTA_MONITORADA}
📁 Organizando: {PASTA_DESTINO}"""
        
        tk.Label(parent, text=info_text, bg="#2d2d2d", fg="#ffffff", justify=tk.LEFT).pack(pady=15, padx=15)
        
        stats_frame = tk.Frame(parent, bg="#2d2d2d")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.stats_labels = {}
        row = 0
        col = 0
        
        for categoria in list(CATEGORIAS.keys()) + ["Outros"]:
            frame = tk.Frame(stats_frame, bg="#333333", relief=tk.RAISED, bd=1)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            tk.Label(frame, text=f"📦 {categoria}", bg="#333333", fg="#42a5f5", 
                    font=("Arial", 9, "bold")).pack(padx=10, pady=(10, 5))
            
            label = tk.Label(frame, text="0", bg="#333333", fg="#42a5f5", font=("Arial", 18, "bold"))
            label.pack(padx=10, pady=(5, 10))
            
            self.stats_labels[categoria] = label
            
            stats_frame.grid_columnconfigure(col, weight=1)
            stats_frame.grid_rowconfigure(row, weight=1)
            
            col += 1
            if col > 3:
                col = 0
                row += 1
    
    def criar_log(self, parent):
        tk.Label(parent, text="📋 Log:", bg="#2d2d2d", fg="#ffffff").pack(pady=(15, 5), padx=15, anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(parent, bg="#333333", fg="#00ff00", 
                                                  font=("Courier", 9), height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        button_frame = tk.Frame(parent, bg="#2d2d2d")
        button_frame.pack(fill=tk.X, padx=15, pady=(5, 15))
        
        tk.Button(button_frame, text="🗑️ Limpar", bg="#666666", fg="white", relief=tk.FLAT,
                 command=lambda: self.log_text.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=5)
    
    def criar_config(self, parent):
        text = f"""📂 Pasta Monitorada:
{PASTA_MONITORADA}

📁 Pasta Destino:
{PASTA_DESTINO}

📦 Categorias:
"""
        for cat, ext in CATEGORIAS.items():
            text += f"\n{cat}: {', '.join(ext)}"
        
        tk.Label(parent, text=text, bg="#2d2d2d", fg="#ffffff", justify=tk.LEFT, 
                font=("Courier", 8)).pack(padx=15, pady=15)
    
    def arquivo_movido(self, nome, categoria):
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[{timestamp}] ✅ {nome} → {categoria}\n"
        self.log_text.insert(tk.END, msg)
        self.log_text.see(tk.END)
        
        if categoria in self.stats_labels:
            numero = int(self.stats_labels[categoria].cget("text"))
            self.stats_labels[categoria].config(text=str(numero + 1))
    
    def iniciar_monitor(self):
        self.monitor_thread = MonitorEmThread(self.arquivo_movido)
        self.monitor_thread.start()
    
    def atualizar(self):
        for categoria in list(CATEGORIAS.keys()) + ["Outros"]:
            pasta = os.path.join(PASTA_DESTINO, categoria)
            if os.path.exists(pasta):
                self.stats_labels[categoria].config(text=str(len(os.listdir(pasta))))
    
    def abrir_pasta(self):
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        if os.name == 'nt':
            os.startfile(PASTA_DESTINO)
        else:
            os.system(f'open "{PASTA_DESTINO}"')
    
    def fechar(self):
        if messagebox.askokcancel("Sair", "Tem certeza?"):
            if self.monitor_thread:
                self.monitor_thread.parar()
            self.root.destroy()

# ============================================
# SYSTEM TRAY
# ============================================

def criar_icone():
    imagem = Image.new('RGB', (64, 64), color=(66, 165, 245))
    draw = ImageDraw.Draw(imagem)
    draw.rectangle([15, 15, 49, 49], outline=(255, 255, 255), width=3)
    return imagem

def mostrar_janela(icon, item, janela):
    janela.root.deiconify()
    janela.root.lift()

def abrir_organizador(icon, item):
    os.makedirs(PASTA_DESTINO, exist_ok=True)
    if os.name == 'nt':
        os.startfile(PASTA_DESTINO)
    else:
        os.system(f'open "{PASTA_DESTINO}"')

def abrir_downloads(icon, item):
    if os.name == 'nt':
        os.startfile(PASTA_MONITORADA)
    else:
        os.system(f'open "{PASTA_MONITORADA}"')

def sair_tray(icon, item, janela):
    icon.stop()
    janela.fechar()

def executar_tray(janela):
    menu = pystray.Menu(
        pystray.MenuItem("🪟 Abrir Janela", lambda icon, item: mostrar_janela(icon, item, janela)),
        pystray.MenuItem("📁 Organizador", abrir_organizador),
        pystray.MenuItem("📂 Downloads", abrir_downloads),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("🛑 Sair", lambda icon, item: sair_tray(icon, item, janela)),
    )
    
    icon = pystray.Icon("Organizador", criar_icone(), menu=menu)
    icon.run()

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#1e1e1e")
    
    janela = JanelaPrincipal(root)
    
    tray_thread = threading.Thread(target=executar_tray, args=(janela,), daemon=True)
    tray_thread.start()
    
    print("=" * 50)
    print("🚀 ORGANIZADOR DE DOWNLOADS v3.0")
    print("=" * 50)
    print(f"📂 Monitorando: {PASTA_MONITORADA}")
    print(f"📁 Organizando: {PASTA_DESTINO}")
    print("✅ GUI + Tray iniciados!")
    print("=" * 50 + "\n")
    
    root.mainloop()