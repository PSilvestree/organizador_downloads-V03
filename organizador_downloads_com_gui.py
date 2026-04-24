import threading
import time
import os
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from PIL import Image, ImageDraw
import pystray
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification

# PyQt5
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QFrame, QScrollArea, QGridLayout, QSpinBox,
                             QCheckBox, QComboBox, QDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QIcon, QColor, QFont, QPixmap
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtCore import QSize

# ============================================
# CONFIGURAÇÕES INICIAIS
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
# SINAIS PARA GUI (Thread-safe)
# ============================================

class Sinais(QObject):
    arquivo_movido = pyqtSignal(str, str)  # nome, categoria
    erro = pyqtSignal(str)
    status_atualizado = pyqtSignal(str)

sinais = Sinais()

# ============================================
# MONITOR DE ARQUIVOS
# ============================================

class OrganizadorArquivos(FileSystemEventHandler):
    def __init__(self):
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
            
            # Atualizar contador
            self.contador[categoria] += 1
            
            # Emitir sinal para GUI
            sinais.arquivo_movido.emit(nome_arquivo, categoria)
            
            # Notificação
            notification.notify(
                title="✅ Arquivo Organizado!",
                message=f"{nome_arquivo}\n📁 {categoria}",
                timeout=5,
                app_name="Organizador de Downloads"
            )
            
        except Exception as e:
            sinais.erro.emit(str(e))

# ============================================
# THREAD DO MONITOR
# ============================================

class MonitorEmThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.observer = None
        self.rodando = True
    
    def run(self):
        self.observer = Observer()
        handler = OrganizadorArquivos()
        self.observer.schedule(handler, PASTA_MONITORADA, recursive=False)
        self.observer.start()
        
        sinais.status_atualizado.emit("✅ Monitor Ativo")
        
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
# JANELA PRINCIPAL (PyQt5)
# ============================================

class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📥 Organizador de Downloads")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(self.estilo_dark())
        
        # Ícone
        self.setWindowIcon(self.criar_icone())
        
        # Monitor
        self.monitor_thread = None
        self.handler = None
        
        # Conectar sinais
        sinais.arquivo_movido.connect(self.on_arquivo_movido)
        sinais.erro.connect(self.on_erro)
        sinais.status_atualizado.connect(self.on_status_atualizado)
        
        # Criar UI
        self.criar_ui()
        self.iniciar_monitor()
    
    def estilo_dark(self):
        return """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
        }
        QPushButton {
            background-color: #42a5f5;
            color: white;
            border: none;
            padding: 8px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #64b5f6;
        }
        QPushButton:pressed {
            background-color: #2196f3;
        }
        QTextEdit, QTableWidget {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #404040;
        }
        QTabWidget::pane {
            border: 1px solid #404040;
        }
        QTabBar::tab {
            background-color: #404040;
            color: #ffffff;
            padding: 8px;
        }
        QTabBar::tab:selected {
            background-color: #42a5f5;
        }
        """
    
    def criar_icone(self):
        # Cria ícone em memória
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(66, 165, 245))
        return QIcon(pixmap)
    
    def criar_ui(self):
        """Cria a interface do usuário"""
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        layout = QVBoxLayout(widget_central)
        
        # ===== HEADER =====
        header = self.criar_header()
        layout.addWidget(header)
        
        # ===== TABS =====
        tabs = QTabWidget()
        tabs.addTab(self.criar_tab_dashboard(), "📊 Dashboard")
        tabs.addTab(self.criar_tab_log(), "📋 Log de Eventos")
        tabs.addTab(self.criar_tab_configuracoes(), "⚙️ Configurações")
        
        layout.addWidget(tabs)
        
        # ===== FOOTER =====
        footer = self.criar_footer()
        layout.addWidget(footer)
    
    def criar_header(self):
        """Header com informações principais"""
        frame = QFrame()
        frame.setStyleSheet("background-color: #2d2d2d; border-bottom: 1px solid #404040;")
        layout = QHBoxLayout(frame)
        
        # Título
        titulo = QLabel("📥 Organizador de Downloads v2.0")
        titulo_font = QFont()
        titulo_font.setPointSize(14)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        layout.addWidget(titulo)
        
        layout.addStretch()
        
        # Status
        self.status_label = QLabel("🔄 Inicializando...")
        status_font = QFont()
        status_font.setPointSize(10)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)
        
        return frame
    
    def criar_tab_dashboard(self):
        """Tab com estatísticas em tempo real"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ===== INFORMAÇÕES =====
        info_layout = QGridLayout()
        
        # Pasta monitorada
        info_layout.addWidget(QLabel("📂 Monitorando:"), 0, 0)
        info_layout.addWidget(QLabel(PASTA_MONITORADA), 0, 1)
        
        # Pasta destino
        info_layout.addWidget(QLabel("📁 Organizando em:"), 1, 0)
        info_layout.addWidget(QLabel(PASTA_DESTINO), 1, 1)
        
        # Data/hora
        info_layout.addWidget(QLabel("🕐 Última atualização:"), 2, 0)
        self.hora_label = QLabel(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        info_layout.addWidget(self.hora_label, 2, 1)
        
        layout.addLayout(info_layout)
        
        # ===== ESTATÍSTICAS =====
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        self.stats_widgets = {}
        col = 0
        for categoria in list(CATEGORIAS.keys()) + ["Outros"]:
            stat_frame = QFrame()
            stat_frame.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
            stat_layout = QVBoxLayout(stat_frame)
            
            # Ícone/Nome
            nome_label = QLabel(f"📦 {categoria}")
            nome_font = QFont()
            nome_font.setBold(True)
            nome_label.setFont(nome_font)
            stat_layout.addWidget(nome_label)
            
            # Número
            numero_label = QLabel("0")
            numero_font = QFont()
            numero_font.setPointSize(20)
            numero_font.setBold(True)
            numero_font.setFamily("Courier")
            numero_label.setFont(numero_font)
            numero_label.setStyleSheet("color: #42a5f5;")
            stat_layout.addWidget(numero_label)
            
            self.stats_widgets[categoria] = numero_label
            
            stats_layout.addWidget(stat_frame, col // 4, col % 4)
            col += 1
        
        layout.addLayout(stats_layout)
        layout.addStretch()
        
        return widget
    
    def criar_tab_log(self):
        """Tab com log de eventos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título
        layout.addWidget(QLabel("📋 Log de Arquivos Organizados:"))
        
        # Log text edit
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(400)
        layout.addWidget(self.log_text)
        
        # Botões
        button_layout = QHBoxLayout()
        
        btn_limpar = QPushButton("🗑️ Limpar Log")
        btn_limpar.clicked.connect(self.limpar_log)
        button_layout.addWidget(btn_limpar)
        
        btn_exportar = QPushButton("💾 Exportar Log")
        btn_exportar.clicked.connect(self.exportar_log)
        button_layout.addWidget(btn_exportar)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget
    
    def criar_tab_configuracoes(self):
        """Tab de configurações"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ===== PASTA MONITORADA =====
        layout.addWidget(QLabel("📂 Configurações"))
        
        config_layout = QGridLayout()
        config_layout.setSpacing(10)
        
        config_layout.addWidget(QLabel("Pasta Monitorada:"), 0, 0)
        pasta_input = QLabel(PASTA_MONITORADA)
        config_layout.addWidget(pasta_input, 0, 1)
        
        btn_abrir_pasta = QPushButton("📂 Abrir Pasta")
        btn_abrir_pasta.clicked.connect(self.abrir_pasta_monitorada)
        config_layout.addWidget(btn_abrir_pasta, 0, 2)
        
        config_layout.addWidget(QLabel("Pasta de Destino:"), 1, 0)
        destino_input = QLabel(PASTA_DESTINO)
        config_layout.addWidget(destino_input, 1, 1)
        
        btn_abrir_destino = QPushButton("📁 Abrir Destino")
        btn_abrir_destino.clicked.connect(self.abrir_pasta_destino)
        config_layout.addWidget(btn_abrir_destino, 1, 2)
        
        layout.addLayout(config_layout)
        
        # ===== CATEGORIAS =====
        layout.addWidget(QLabel("\n📦 Categorias Ativas:"))
        
        cat_text = QTextEdit()
        cat_text.setReadOnly(True)
        cat_text.setMaximumHeight(200)
        
        cat_info = ""
        for categoria, extensoes in CATEGORIAS.items():
            cat_info += f"📦 {categoria}:\n   {', '.join(extensoes)}\n\n"
        
        cat_text.setText(cat_info)
        layout.addWidget(cat_text)
        
        # ===== SOBRE =====
        layout.addWidget(QLabel("\n❓ Sobre:"))
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setMaximumHeight(150)
        about_text.setText("""
📥 Organizador de Downloads v2.0

Um aplicativo que organiza automaticamente seus downloads
em categorias usando Threading e System Tray.

🔧 Tecnologias:
  • Python 3.7+
  • PyQt5 (Interface Gráfica)
  • PySTray (System Tray)
  • Watchdog (File Monitoring)
  • Threading (Processamento Paralelo)

👨‍💻 Desenvolvido para Portfolio
        """)
        layout.addWidget(about_text)
        
        layout.addStretch()
        
        return widget
    
    def criar_footer(self):
        """Footer com botões de ação"""
        frame = QFrame()
        frame.setStyleSheet("background-color: #2d2d2d; border-top: 1px solid #404040;")
        layout = QHBoxLayout(frame)
        
        btn_refresh = QPushButton("🔄 Atualizar")
        btn_refresh.clicked.connect(self.atualizar_dashboard)
        layout.addWidget(btn_refresh)
        
        btn_abrir_org = QPushButton("📁 Abrir Organizador")
        btn_abrir_org.clicked.connect(self.abrir_pasta_destino)
        layout.addWidget(btn_abrir_org)
        
        layout.addStretch()
        
        btn_minimizar = QPushButton("➖ Minimizar")
        btn_minimizar.clicked.connect(self.hide)
        layout.addWidget(btn_minimizar)
        
        btn_sair = QPushButton("🛑 Sair")
        btn_sair.clicked.connect(self.close)
        layout.addWidget(btn_sair)
        
        return frame
    
    def iniciar_monitor(self):
        """Inicia a thread de monitoramento"""
        self.monitor_thread = MonitorEmThread()
        self.monitor_thread.start()
        
        self.handler = OrganizadorArquivos()
    
    def on_arquivo_movido(self, nome, categoria):
        """Callback quando arquivo é movido"""
        # Atualizar log
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[{timestamp}] ✅ {nome} → {categoria}\n"
        self.log_text.insertPlainText(msg)
        
        # Scroll até o fim
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
        # Atualizar estatísticas
        if categoria in self.stats_widgets:
            numero = int(self.stats_widgets[categoria].text())
            self.stats_widgets[categoria].setText(str(numero + 1))
        
        # Atualizar hora
        self.hora_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    def on_erro(self, erro):
        """Callback quando há erro"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[{timestamp}] ❌ Erro: {erro}\n"
        self.log_text.insertPlainText(msg)
    
    def on_status_atualizado(self, status):
        """Callback de status"""
        self.status_label.setText(status)
    
    def atualizar_dashboard(self):
        """Atualiza estatísticas"""
        for categoria in list(CATEGORIAS.keys()) + ["Outros"]:
            pasta = os.path.join(PASTA_DESTINO, categoria)
            if os.path.exists(pasta):
                quantidade = len(os.listdir(pasta))
                self.stats_widgets[categoria].setText(str(quantidade))
    
    def limpar_log(self):
        """Limpa o log"""
        self.log_text.clear()
    
    def exportar_log(self):
        """Exporta log para arquivo"""
        try:
            path = os.path.join(PASTA_DESTINO, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())
            
            QMessageBox.information(self, "Sucesso", f"Log exportado para:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar: {e}")
    
    def abrir_pasta_monitorada(self):
        """Abre pasta monitorada"""
        if os.name == 'nt':
            os.startfile(PASTA_MONITORADA)
        else:
            os.system(f'open "{PASTA_MONITORADA}"')
    
    def abrir_pasta_destino(self):
        """Abre pasta de destino"""
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        if os.name == 'nt':
            os.startfile(PASTA_DESTINO)
        else:
            os.system(f'open "{PASTA_DESTINO}"')
    
    def closeEvent(self, event):
        """Ao fechar a janela"""
        self.hide()
        event.ignore()

# ============================================
# SYSTEM TRAY
# ============================================

class AplicacaoTray:
    def __init__(self, janela):
        self.janela = janela
    
    def criar_menu(self):
        """Menu do tray icon"""
        return pystray.Menu(
            pystray.MenuItem("🪟 Abrir Janela", self.mostrar_janela),
            pystray.MenuItem("📁 Abrir Organizador", self.abrir_pasta),
            pystray.MenuItem("📂 Abrir Downloads", self.abrir_downloads),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🛑 Sair", self.sair),
        )
    
    def mostrar_janela(self, icon, item):
        """Mostra a janela"""
        self.janela.showNormal()
        self.janela.activateWindow()
    
    def abrir_pasta(self, icon, item):
        """Abre pasta organizador"""
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        if os.name == 'nt':
            os.startfile(PASTA_DESTINO)
        else:
            os.system(f'open "{PASTA_DESTINO}"')
    
    def abrir_downloads(self, icon, item):
        """Abre downloads"""
        if os.name == 'nt':
            os.startfile(PASTA_MONITORADA)
        else:
            os.system(f'open "{PASTA_MONITORADA}"')
    
    def sair(self, icon, item):
        """Sair da aplicação"""
        print("🛑 Encerrando...")
        self.janela.close()
        icon.stop()
    
    def executar_tray(self):
        """Inicia o tray icon"""
        icone = self.criar_icone_tray()
        
        icon = pystray.Icon(
            name="Organizador Downloads",
            icon=icone,
            title="Organizador de Downloads",
            menu=self.criar_menu()
        )
        
        icon.run()
    
    @staticmethod
    def criar_icone_tray():
        """Cria ícone azul para tray"""
        imagem = Image.new('RGB', (64, 64), color=(66, 165, 245))
        draw = ImageDraw.Draw(imagem)
        draw.rectangle([15, 15, 49, 49], outline=(255, 255, 255), width=3)
        return imagem

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    app_qt = QApplication([])
    
    # Criar janela principal
    janela = JanelaPrincipal()
    janela.show()
    
    # Criar tray
    tray_app = AplicacaoTray(janela)
    
    # Rodas tray em thread
    tray_thread = threading.Thread(target=tray_app.executar_tray, daemon=True)
    tray_thread.start()
    
    # Executar Qt
    app_qt.exec_()
