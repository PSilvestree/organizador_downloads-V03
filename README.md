# 📁 Organizador de Downloads - V03

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

Ferramenta automática desenvolvida em Python para organizar, categorizar e renomear arquivos de forma inteligente. Ideal para manter fluxos de trabalho acadêmicos e profissionais estruturados, eliminando a desordem da pasta de downloads com regras customizáveis.

## 🎯 Funcionalidades
* **🗂️ Organização Inteligente:** Categorização automática por extensão (Documentos, Imagens, Vídeos, etc).
* **✏️ Gestão de Nomes:** Renomeação em massa com padrões customizáveis.
* **📅 Agrupamento Temporal:** Organização de arquivos por data de criação ou modificação.
* **🔍 Limpeza de Disco:** Detecção e remoção de duplicatas e arquivamento de itens antigos (>90 dias).
* **⚙️ Automação (Watchdog):** Monitoramento em tempo real da pasta (agendamento diário/horário).
* **📊 Governança:** Geração de relatórios de operação e função de "Desfazer" (Undo).

## 🛠️ Tecnologias
* **Python 3.8+**
* **Bibliotecas Chave:** `pathlib` (gestão de caminhos), `shutil` (operação de arquivos), `schedule` (automação), `watchdog` (monitoramento de eventos).

## 📦 Instalação
```bash
# Clone o repositório
git clone [https://github.com/PSilvestree/organizador_downloads-V03.git](https://github.com/PSilvestree/organizador_downloads-V03.git)
cd organizador_downloads-V03

# Instale as dependências
pip install -r requirements.txt
```

## 🚀 Como Usar

### Interface CLI
```bash
python main.py
```
Ao iniciar, o menu interativo permitirá escolher entre organizar agora, configurar novas regras ou verificar relatórios de espaço liberado.

### Configuração (`config.json`)
Você pode definir suas próprias extensões e destinos:
```json
{
  "pasta_downloads": "C:\\Users\\Paulo\\Downloads",
  "estrutura_pastas": {
    "Pesquisa_UEM": [".pdf", ".docx", ".xlsx"],
    "Midia": [".jpg", ".png", ".mp4"]
  },
  "remover_duplicatas": true
}
```

## 📊 Exemplo de Estrutura Gerada
```text
Downloads/
├── Documentos/
│   ├── Relatório_Mestrado_2026.pdf
│   └── Planilha_Pesquisa.xlsx
├── Imagens/
│   └── Screenshot_2026-04-25.png
└── Arquivos_Antigos/ (Movidos automaticamente após 90 dias)
```

## 📈 Roadmap de Versões
| Versão | Status | Principais Implementações |
|:---:|:---:|:---|
| **v0.3** | Atual | Agendamento, relatórios HTML e histórico de operações. |
| **v0.2** | Estável | Remoção de duplicatas e lógica de arquivamento. |
| **v0.1** | Inicial | Script básico de movimentação por extensão. |

## 📄 Licença
Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

🔗 [LinkedIn](https://www.linkedin.com/in/paulosilvestree)
```
