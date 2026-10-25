1 Criar pasta e ambiente virtual (.venv)
    1.1 – criar um ambiente virtual: python –m venv .venv
    1.2 – ativar ele:  em Scripts > activate
    1.3 – Instalar o Django > pip install django
    1.4 – Colocar requerimentos pip freeze >  pip freeze  install  > requeriments.txt
    1.5 – criamos as configs e o projeto:  django-admin startproject CIA   . / python manage.py startapp AMOVE
    1.6 – então seguimos para a parte de “codar”

    Começamos com a utilização de IA - nessa etapa utilizamos a seguinte estratégia passávamos a idéia do que queríamos para o ChatGPT e depois ele gerava um prompt para colocarmos no Copilot, dessa forma conseguimos otimizar o que era pedido diminuindo o número de erros e conseguindo detalhar bem as alterações.

2 - Quando digitado "/turmas" na URL do navegador, a pasta urls.py do projeto(AMOVE) é acionada ela identifica a URL padrão já pré definida e redireciona para a pasta do projeto views.py, logo em seguida é exibida a informação. Funciona como um sistema de rotas e entregas, a urls.py recebe o pedido do usuário e chama a view correspondente para processar a resposta. Já os dados vem do banco de dados, mas as informações que aparecem, estão em um arquivo chamado “models.py”.

3 - O makemigrations entende como foi alterado o models.py e cria arquivos com as instruções para modificar o banco de dados. Já o migrate aplica essas instruções e aplica as alterações no banco de dados.
Se rodarmos apenas makemigrations os arquivos serão criados, mas as alterações ainda não serão aplicadas ao banco de dados.

4 - A chave estrangeira evita repetir o nome da modalidade em cada turma e mantém o relacionamento com um cadastro único (unique=True). se fosse salvo como texto existiriam diversas variáveis. a modalidade musculação poderia ser escrita de diversas formas diferentes “musculaçao”; “Musculaçao”;”Musculação”.

5 - Não será possível pois existe um código que impede essa ação, ‘on_delete=models.PROTECT’;  escolhemos essa opção porque foi solicitado assim.

6 - O dia da semana vem de uma lista fixa, pois assim poupa tempo de ter que ajustar como cada indivíduo escreveu o nome da semana.

7 - list_display: define as colunas da listagem. / list_filter: disponibiliza filtros laterais / search_fields: configura a busca por texto. ou seja sem eles ainda existiria um funcionamento, mas perderia toda praticidade.

8 - quando usamos o código ‘for modalidade in Modalidade.objects.filter(ativa=True):’ ele faz um laço de repetição verificando as modalidades (definidas pelo usuário), dentro da classe modalidade e faz uma varredura dos itens ativos através da ForeignKey(ativa=True).

9 - Não tivemos problemas com o Copilot pelo método adotado com ChatGPT.

10 - Colocamos um layout no painel administrativo, acrescentamos um item clicável na homepage (somente para usuários admins cadastrados), que permitia transitar diretamente sem usar a URLS, para ir para o cadastro de turmas e painel administrativo.

11 - Aprendemos principalmente, criar e dividir ambientes e atividades em que cada integrante pudesse alterar e editar. Usando o GIT e GITHUB. E como faríamos isso. O uso de inteligência artificial e até onde precisamos consultar a I.A. E também, a introdução ao http tendo já uma experiência de interação com o usuário final.