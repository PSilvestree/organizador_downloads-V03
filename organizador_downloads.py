import threading
import time
import os
import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw
import pystray
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification

# ============================================
# CONFIGURAÇÕES INICIAIS
# ============================================

# 👇 MUDE ESTE CAMINHO PARA ONDE SEUS ARQUIVOS DESCEM
PASTA_MONITORADA = os.path.expanduser("~/Downloads")

# Pasta onde os arquivos serão organizados
PASTA_DESTINO = os.path.expanduser("~/Organizador")

# Extensões de arquivo por categoria
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
# CLASSE PARA MONITORAR ARQUIVO
# ============================================

class OrganizadorArquivos(FileSystemEventHandler):
    """Monitora pasta e organiza arquivos automaticamente"""
    
    def on_created(self, event):
        """Disparado quando um arquivo é criado/movido para a pasta"""
        if not event.is_directory:
            time.sleep(1)  # Espera 1 segundo para arquivo ficar pronto
            self.organizar_arquivo(event.src_path)
    
    def on_modified(self, event):
        """Disparado quando arquivo é modificado (pode ser download terminando)"""
        if not event.is_directory:
            # Ignora modificações muito rápidas
            time.sleep(0.5)
            # Só organiza se arquivo > 1MB (provavelmente download completo)
            try:
                if os.path.getsize(event.src_path) > 1024 * 1024:
                    self.organizar_arquivo(event.src_path)
            except:
                pass
    
    def organizar_arquivo(self, caminho_arquivo):
        """Organiza um arquivo em sua categoria correspondente"""
        try:
            # Ignora arquivos ocultos/temporários
            nome_arquivo = os.path.basename(caminho_arquivo)
            if nome_arquivo.startswith(".") or nome_arquivo.endswith(".part"):
                return
            
            # Aguarda arquivo ficar disponível (não travado por outro processo)
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
            
            # Obtém extensão do arquivo
            _, extensao = os.path.splitext(nome_arquivo)
            extensao = extensao.lower()
            
            # Encontra categoria
            categoria = "Outros"
            for cat, extensoes in CATEGORIAS.items():
                if extensao in extensoes:
                    categoria = cat
                    break
            
            # Cria pasta de destino se não existir
            pasta_categoria = os.path.join(PASTA_DESTINO, categoria)
            os.makedirs(pasta_categoria, exist_ok=True)
            
            # Move arquivo
            caminho_destino = os.path.join(pasta_categoria, nome_arquivo)
            
            # Se arquivo já existe, renomeia
            contador = 1
            nome_base, ext = os.path.splitext(nome_arquivo)
            while os.path.exists(caminho_destino):
                novo_nome = f"{nome_base}_{contador}{ext}"
                caminho_destino = os.path.join(pasta_categoria, novo_nome)
                contador += 1
            
            # Move o arquivo
            shutil.move(caminho_arquivo, caminho_destino)
            
            # Envia notificação
            self.notificar_sucesso(nome_arquivo, categoria)
            
        except Exception as e:
            self.notificar_erro(str(e))
    
    def notificar_sucesso(self, nome_arquivo, categoria):
        """Envia notificação de sucesso"""
        notification.notify(
            title="✅ Arquivo Organizado!",
            message=f"{nome_arquivo}\n📁 Movido para: {categoria}",
            timeout=5,
            app_name="Organizador de Downloads"
        )
        print(f"✅ {nome_arquivo} → {categoria}")
    
    def notificar_erro(self, erro):
        """Envia notificação de erro"""
        notification.notify(
            title="❌ Erro ao Organizar",
            message=f"Erro: {erro[:50]}...",
            timeout=5,
            app_name="Organizador de Downloads"
        )
        print(f"❌ Erro: {erro}")

# ============================================
# FUNÇÃO PARA CRIAR ÍCONE AUTOMÁTICO
# ============================================

def criar_icone_generico():
    """Gera um ícone azul genérico em memória"""
    # Cria imagem 64x64 com fundo azul
    imagem = Image.new('RGB', (64, 64), color=(66, 165, 245))
    
    # Desenha um quadrado branco no meio
    draw = ImageDraw.Draw(imagem)
    draw.rectangle([15, 15, 49, 49], outline=(255, 255, 255), width=3)
    
    return imagem

# ============================================
# THREADING - MONITOR EM BACKGROUND
# ============================================

class MonitorEmThread(threading.Thread):
    """Thread que roda o monitor de arquivos"""
    
    def __init__(self):
        super().__init__(daemon=True)
        self.observer = None
    
    def run(self):
        """Inicia o monitor"""
        print(f"🔍 Monitorando pasta: {PASTA_MONITORADA}")
        
        # Cria observer
        self.observer = Observer()
        
        # Registra pasta a monitorar
        handler = OrganizadorArquivos()
        self.observer.schedule(handler, PASTA_MONITORADA, recursive=False)
        
        # Inicia
        self.observer.start()
        print("✅ Monitor ativo!")
        
        # Mantém a thread rodando
        try:
            while self.observer.is_alive():
                self.observer.join(timeout=1)
        except KeyboardInterrupt:
            self.parar()
    
    def parar(self):
        """Para o monitor"""
        if self.observer:
            self.observer.stop()
            self.observer.join()

# ============================================
# SYSTEM TRAY - ÍCONE NA BANDEJA
# ============================================

class AplicacaoTray:
    def __init__(self):
        self.monitor_thread = None
        self.ativo = True
    
    def iniciar_monitor(self):
        """Inicia a thread do monitor"""
        self.monitor_thread = MonitorEmThread()
        self.monitor_thread.start()
    
    def sair(self, icon, item):
        """Encerra a aplicação"""
        self.ativo = False
        print("🛑 Encerrando...")
        
        try:
            if self.monitor_thread and self.monitor_thread.observer:
                self.monitor_thread.parar()
        except Exception as e:
            print(f"⚠️  Aviso ao encerrar monitor: {e}")
        
        icon.stop()
        print("✅ Aplicação encerrada com sucesso!")
    
    def criar_menu(self):
        """Menu do tray icon"""
        return pystray.Menu(
            pystray.MenuItem("📁 Abrir Organizador", self.abrir_pasta),
            pystray.MenuItem("📂 Abrir Downloads", self.abrir_downloads),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🛑 Sair", self.sair),
        )
    
    def abrir_pasta(self, icon, item):
        """Abre pasta de destino"""
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        if os.name == 'nt':  # Windows
            os.startfile(PASTA_DESTINO)
        elif os.name == 'posix':  # macOS/Linux
            os.system(f'open "{PASTA_DESTINO}"')
    
    def abrir_downloads(self, icon, item):
        """Abre pasta de downloads"""
        if os.name == 'nt':
            os.startfile(PASTA_MONITORADA)
        elif os.name == 'posix':
            os.system(f'open "{PASTA_MONITORADA}"')
    
    def executar(self):
        """Inicia a aplicação com ícone na bandeja"""
        # Inicia o monitor ANTES do ícone
        self.iniciar_monitor()
        
        # Cria ícone genérico
        icone = criar_icone_generico()
        
        # Configura e mostra ícone
        icon = pystray.Icon(
            name="Organizador Downloads",
            icon=icone,
            title="Organizador de Downloads",
            menu=self.criar_menu()
        )
        
        # Executa o ícone
        icon.run()

# ============================================
# PONTO DE ENTRADA
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 ORGANIZADOR DE DOWNLOADS v1.0")
    print("=" * 50)
    print(f"📂 Monitorando: {PASTA_MONITORADA}")
    print(f"📁 Organizando em: {PASTA_DESTINO}")
    print("\n💡 Clique com botão direito no ícone azul")
    print("   para acessar o menu!")
    print("=" * 50 + "\n")
    
    try:
        app = AplicacaoTray()
        app.executar()
    except KeyboardInterrupt:
        print("\n🛑 Aplicação encerrada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
