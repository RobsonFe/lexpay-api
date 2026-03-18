from crewai import Agent, Task, Crew, LLM

# 1. Configuração do Modelo (Certifique-se de que o Ollama está rodando!)
ollama_llm = LLM(
    model="ollama/qwen2.5-coder:1.5b",
    base_url="http://localhost:11434"
)

# 2. Definição do Agente
engenheiro = Agent(
    role="Arquiteto de Software Backend",
    goal="Desenvolver a estrutura de uma API robusta para o projeto LexPay",
    backstory="Você é um especialista em Python, Django e PostgreSQL, focado em sistemas financeiros.",
    llm=ollama_llm,
    verbose=True
)

# 3. Definição da Tarefa (Task)
tarefa_teste = Task(
    description=(
        "Crie uma estrutura inicial de classes em Python para uma API de Precatórios. "
        "A classe deve conter campos como: numero_processo, valor_original e beneficiario. "
        "Use o padrão do Django Models."
    ),
    expected_output="Um arquivo Python contendo a classe do Django Model bem estruturada.",
    agent=engenheiro
)

# 4. Montagem do Crew (A Equipe)
equipe_lexpay = Crew(
    agents=[engenheiro],
    tasks=[tarefa_teste],
    verbose=True
)

# 5. Execução
print("\n--- Iniciando a execução do Agente com Ollama ---")
resultado = equipe_lexpay.kickoff()

print("\n\n--- RESULTADO FINAL DO ENGENHEIRO ---")
print(resultado)