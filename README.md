# EVOA

**Ecologia - Vigilância - Organização - Ação**  

Alinhado ao Objetivo de Desenvolvimento Sustentável número 12 da ONU, que se refere ao consumo e produção responsáveis. O **EVOA** é um aplicativo que busca incentivar a **reciclagem** e a **consciência ambiental** através de um sistema de recompensas e gamificação.
Os usuários podem registrar materiais reciclados, acumular **Cash** e **XP**, acompanhar seu histórico e evoluir de nível dentro da plataforma, além de contar uma funcionalidade de denúncias de problemas infraestruturais urbanos.

---

## Funcionalidades Principais
- **Registro de Reciclagem**: registre materiais reciclados (plástico, papel, vidro, metal, eletrônicos e outros).
- **Sistema de Cash**: cada reciclagem gera Cash acumulado no perfil do usuário.  
- **Progressão por Nível**: acumule XP ao reciclar e suba de nível.  
- **Ranking**: compare sua evolução com outros usuários.
- **Loja**: utilize o Cash acumulado para recompensas futuras.
- **Histórico Diário**: acompanhe quanto reciclou e quanto obteve em Cash e XP em cada dia.
- **Denúncias**: denuncie falhas, danos e dentre outros problemas na infraestrutura da cidade.

---

## Autores
- Matheus Teles de Andrade
- João Pedro Oliveira Campos
- Felipe Marcondes Corcini
- Camilly Luana Lauer
- Djalma Alves Galli Cavalheiro
- Lucas Gomes Machado
- Gabriel Ruan Nepumoceno

---

## Estrutura do Projeto
O EVOA é construído em **Flask**, permitindo, a princípio, a execução na Web.  
Alguns módulos já implementados:  
- **/profile** → visão geral do perfil, Cash e XP.

---

## Pré-visualizações
> *(Prints da aplicação ou gravações de tela quando disponíveis)*  

- **Exemplo de perfil do usuário**  
  ![Imagem Perfil](docs/images/perfil.png)  

- **Exemplo de registro de material**  
  ![Imagem Registro](docs/images/registro.png)  

- **Demonstração em vídeo**  
  [![Assista ao vídeo](docs/images/video_thumb.png)](docs/videos/demo.mp4)  

---

## Documentos
- https://drive.google.com/drive/folders/1xgoAVzVvhmDfbeCC2Tol_XpRYIur1hLu?usp=sharing

## 🔧 Instalação e Execução
1. Clone este repositório:  
   ```bash
   git clone https://github.com/math490/EVOA.git

2. No terminal do vscode crie um ambiente virtual e o ative:  
   ```bash
   python -m venv env
   env/Scripts/activate

3. Instale as dependências do flask:  
   ```bash
   pip install flask
   pip install flask flask-sqlalchemy
   pip install flask-login
