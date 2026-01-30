# Crop Images PNG - Recorte de Bordas Transparentes

Script Python para recortar bordas transparentes de imagens PNG de forma automática e precisa.

## 📋 Descrição

Este projeto contém o script `trim_png_alpha.py` que remove automaticamente as bordas transparentes de imagens PNG, mantendo apenas o conteúdo relevante. O script suporta:

- Processamento de arquivos individuais ou diretórios completos
- Detecção automática de conteúdo com base no canal alfa
- Fallback para imagens sem canal alfa (detectando diferenças em relação ao fundo branco)
- Opções de padding personalizável
- Processamento recursivo de subpastas
- Preservação da estrutura de diretórios

## 🚀 Configuração do Ambiente

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Instalação - Passo a Passo

#### 1. Clone ou baixe este repositório

```bash
cd "E:\Projetos\Python\Crop Images PNG"
```

#### 2. Crie um ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
```

**Windows (CMD):**
```cmd
python -m venv .venv
```

**Linux/Mac:**
```bash
python3 -m venv .venv
```

#### 3. Ative o ambiente virtual

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

Se encontrar erro de política de execução, execute antes:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

Você saberá que o ambiente está ativado quando ver `(.venv)` no início da linha de comando.

#### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

## 💻 Como Usar

### Sintaxe Básica

```bash
python trim_png_alpha.py <caminho_entrada> [opções]
```

### Exemplos de Uso

#### 1. Processar um único arquivo
```bash
python trim_png_alpha.py "planta.png"
```

#### 2. Processar todos os PNGs em uma pasta
```bash
python trim_png_alpha.py "./plants"
```

#### 3. Processar recursivamente com padding
```bash
python trim_png_alpha.py "./plants" --recursive --padding 8
```

#### 4. Especificar diretório de saída
```bash
python trim_png_alpha.py "./plants" --out "./recortadas"
```

#### 5. Simular processamento (dry-run)
```bash
python trim_png_alpha.py "./plants" --recursive --dry-run
```

#### 6. Preservar estrutura de diretórios
```bash
python trim_png_alpha.py "./plants" --recursive --keep-structure
```

### Opções Disponíveis

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `--out` | Diretório de saída | `<pasta_entrada>/trimmed` |
| `--threshold` | Limite do canal alfa (0-254) | 0 |
| `--padding` | Pixels de margem ao redor do conteúdo | 0 |
| `--recursive` | Processar subpastas | Desativado |
| `--overwrite` | Sobrescrever arquivos existentes | Desativado |
| `--keep-structure` | Manter estrutura de pastas | Desativado |
| `--dry-run` | Simular sem gravar arquivos | Desativado |

## 📦 Dependências

- **Pillow** (>=10.0.0): Biblioteca para manipulação de imagens
- **numpy** (>=1.24.0): Biblioteca para operações com arrays numéricos

## 🔄 Atualizando Dependências

Para atualizar as dependências para suas versões mais recentes:

```bash
pip install --upgrade -r requirements.txt
```

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
Crop Images PNG/
├── .venv/                   # Ambiente virtual (não versionado)
├── plants/                  # Pasta de exemplo com imagens
├── trim_png_alpha.py       # Script principal
├── requirements.txt        # Dependências do projeto
├── .gitignore             # Arquivos ignorados pelo Git
└── README.md              # Este arquivo
```

### Desativando o Ambiente Virtual

Quando terminar de trabalhar no projeto:

```bash
deactivate
```

## 📝 Notas Importantes

1. **Sempre ative o ambiente virtual** antes de executar o script ou instalar dependências
2. O diretório `.venv/` não é versionado no Git (está no `.gitignore`)
3. As imagens processadas são salvas em `trimmed/` por padrão (também não versionado)
4. O script preserva o modo de cor original das imagens (RGBA, RGB, etc.)
5. A resolução (DPI) das imagens é mantida quando disponível

## 🐛 Solução de Problemas

### Erro ao ativar ambiente virtual no Windows
- Execute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Erro "módulo não encontrado"
- Certifique-se de que o ambiente virtual está ativado
- Reinstale as dependências: `pip install -r requirements.txt`

### Imagens não são recortadas
- Verifique se a imagem possui canal alfa ou fundo suficientemente diferente de branco
- Tente ajustar o `--threshold` para um valor menor
- Use `--dry-run` para ver o que será processado antes de executar

## 📄 Licença

Este é um projeto pessoal. Use conforme necessário.

## 👤 Autor

Desenvolvido como ferramenta para automatizar o recorte de imagens PNG.
