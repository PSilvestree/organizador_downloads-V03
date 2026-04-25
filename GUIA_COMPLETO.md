# 📖 Guia Completo

## 📊 Interface Visual

```
┌──────────────────────────────────────────┐
│ 📥 Organizador de Downloads              │
├──────────────────────────────────────────┤
│ [📊 Dashboard] [📋 Log] [⚙️ Config]     │
├──────────────────────────────────────────┤
│                                          │
│ 📂 Monitorando: ~/Downloads              │
│ 📁 Organizando: ~/Organizador            │
│                                          │
│ ┌─────┬─────┬─────┬─────┬─────┬─────┐  │
│ │Imgs │PDFs │Docs │Vids │Áud  │Zip  │  │
│ │ 12  │  5  │  8  │  3  │  2  │  1  │  │
│ └─────┴─────┴─────┴─────┴─────┴─────┘  │
│                                          │
│ [🔄] [📁] [➖] [🛑]                    │
└──────────────────────────────────────────┘
```

## 📊 ABA 1: DASHBOARD

Mostra em tempo real:

- **Informações**: Pastas monitoradas
- **Contadores**: Arquivos por categoria
- **Auto-atualização**: Quando arquivo é movido

### Contadores

Cada categoria mostra quantos arquivos tem:
- Imagens: .jpg, .png, .gif, etc
- PDFs: .pdf
- Documentos: .doc, .docx, .xlsx, etc
- Vídeos: .mp4, .avi, .mov, etc
- Áudios: .mp3, .wav, .flac, etc
- Comprimidos: .zip, .rar, .7z, etc
- Executáveis: .exe, .msi, .app, etc
- Código: .py, .js, .html, etc
- Outros: extensões não listadas

## 📋 ABA 2: LOG

Histórico de eventos com timestamps:

```
[14:35:22] ✅ foto.jpg → Imagens
[14:35:45] ✅ documento.pdf → PDFs
[14:36:10] ✅ video.mp4 → Vídeos
[14:36:33] ✅ script.py → Código
```

### Botão 🗑️ Limpar
Remove todo o histórico (não afeta arquivos movidos!)

## ⚙️ ABA 3: CONFIGURAÇÕES

Mostra:

- **Pasta Monitorada**: Onde arquivos descem
- **Pasta Destino**: Onde são organizados
- **Categorias**: Todas as extensões mapeadas

## 🎮 BOTÕES

### Footer da Janela

| Botão | Função |
|-------|--------|
| 🔄 Atualizar | Força refresh dos números |
| 📁 Abrir | Abre pasta organizada |
| ➖ Minimizar | Oculta janela (roda em background) |
| 🛑 Sair | Encerra programa |

### Menu Tray (Botão direito no ícone)

```
🪟 Abrir Janela      → Mostra GUI novamente
📁 Organizador       → Abre pasta final
📂 Downloads         → Abre pasta monitorada
─────────────────
🛑 Sair              → Fecha tudo
```

## ⚙️ CONFIGURAÇÕES

### Mudar Pasta Monitorada

Abra `organizador_downloads_com_gui.py`:

```python
PASTA_MONITORADA = os.path.expanduser("~/Downloads")
```

Mude para:

```python
PASTA_MONITORADA = os.path.expanduser("~/Desktop")
# ou
PASTA_MONITORADA = "/caminho/completo"
```

### Mudar Pasta de Destino

```python
PASTA_DESTINO = os.path.expanduser("~/Meus Documentos Organizados")
```

### Adicionar Nova Categoria

Procure:

```python
CATEGORIAS = {
    "Imagens": [...],
    "PDFs": [...],
    # Adicione aqui:
    "Meus Arquivos": [".xyz", ".abc"],
}
```

### Remover Categoria

Simplesmente delete a linha:

```python
# "PDFs": [".pdf"],  ← Deletar essa linha
```

### Trocar Extensões

```python
# Mover PDFs para Documentos
"Documentos": [".doc", ".docx", ".txt", ".xlsx", ".xls", ".pptx", ".odt", ".pdf"],
"PDFs": [],  # Deixar vazio ou remover
```

## 🔄 FLUXO DE FUNCIONAMENTO

1. **Você coloca arquivo em ~/Downloads**
   ↓
2. **Watchdog detecta o arquivo**
   ↓
3. **Programa identifica a extensão**
   ↓
4. **Encontra a categoria correspondente**
   ↓
5. **Cria pasta se não existir**
   ↓
6. **Move o arquivo**
   ↓
7. **Dashboard atualiza**
   ↓
8. **Log registra**
   ↓
9. **Notificação aparece**

## 🧵 THREADING

O programa roda em 2 threads paralelas:

- **Thread 1**: GUI (janela responsiva)
- **Thread 2**: Monitor (observa pasta)

Isso significa:
- Você pode clicar em botões enquanto arquivo é movido
- GUI nunca trava
- Sem delay na interface

## 📱 SYSTEM TRAY

O ícone azul na bandeja permite:

- **Minimizar janela sem fechar programa**
- **Abrir janela novamente**
- **Menu rápido**
- **Sair corretamente**

### Windows
Procure no canto inferior direito → seta ↑

### macOS
Procure no canto superior direito

### Linux
Varia com gerenciador de janelas

## 🎨 TEMA

Cores do tema dark:

```
Fundo: #1e1e1e (escuro)
Panels: #2d2d2d (cinza)
Botões: #42a5f5 (azul)
Texto: #ffffff (branco)
Log: #00ff00 (verde)
```

Para mudar cores, edite as cores hexadecimais no código.

## 📊 PERFORMANCE

Medições em repouso:

- **CPU**: < 1%
- **Memória**: ~60 MB
- **Startup**: 2-3 segundos

Totalmente aceitável para deixar rodando o dia inteiro!

## 🔐 SEGURANÇA

- ✅ Sem internet
- ✅ Sem telemetria
- ✅ Sem coleta de dados
- ✅ Código local

## 💾 ONDE OS DADOS FICAM

```
Windows:
  Downloads: C:\Users\[User]\Downloads
  Organizador: C:\Users\[User]\Organizador

macOS/Linux:
  Downloads: ~/Downloads
  Organizador: ~/Organizador
```

## 🆘 TROUBLESHOOTING

### Arquivo não foi movido
**Checklist:**
- [ ] Extensão está em CATEGORIAS?
- [ ] Arquivo não está travado?
- [ ] Pasta tem permissão de escrita?
- [ ] Arquivo não é temporário (.tmp, .part)?

### Janela não aparece
```bash
python organizador_downloads_com_gui.py
```
Se nada acontecer, verifique instalação:
```bash
pip install -r requirements.txt
```

### Ícone tray não aparece
- Tray está escondido? (Windows)
- Gerenciador não suporta? (Linux)

### Notificações não funcionam
**Windows:**
- Ative em Configurações → Notificações

**macOS:**
- Privacy & Security → Notificações

**Linux:**
- Install: `sudo apt-get install libnotify-bin`

## 🎓 EXPLICAÇÃO TÉCNICA

### Como funciona

1. **Watchdog** monitora pasta
2. **Callbacks** são disparados
3. **Threads** processam em paralelo
4. **GUI atualiza** via callbacks
5. **Notificações** são enviadas
6. **Log registra** tudo

### Stack Técnico

- **Python 3.7+**
- **Tkinter** - GUI (vem com Python)
- **Watchdog** - Monitor de arquivos
- **PySTray** - System Tray
- **Pillow** - Criar ícone
- **Plyer** - Notificações
- **Threading** - Processamento paralelo

## 🚀 PRÓXIMAS EXPANSÕES

Ideias para melhorar:

**Nível 1 (Fácil):**
- [ ] Adicionar gráficos
- [ ] Toggle tema light/dark
- [ ] Contador de tempo rodando

**Nível 2 (Médio):**
- [ ] Configurar categorias na GUI
- [ ] Salvar config em JSON
- [ ] Database com histórico

**Nível 3 (Avançado):**
- [ ] API REST
- [ ] Cloud sync
- [ ] Executável (.exe, .app)

---

**Perguntas?** Veja o README.md ou QUICK_START.md
