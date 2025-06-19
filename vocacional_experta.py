import collections
import collections.abc
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping

from experta import KnowledgeEngine, Fact, Field, MATCH, Rule, OR

from flask import Flask, request, render_template_string

SYNONYMS_MAP = {
    'matematica': ['numeros', 'calculos', 'matematica', 'matematico', 'estatistica', 'logica', 'equacoes'],
    'fisica': ['fisica', 'leis da natureza', 'energia', 'mecanica', 'eletricidade', 'astronomia'],
    'quimica': ['quimica', 'elementos', 'reacoes', 'moleculas', 'laboratorio', 'substancias'],
    'programacao': ['programacao', 'computacao', 'software', 'coding', 'desenvolvimento', 'algoritmos', 'ti', 'tecnologia', 'sistema', 'sistemas', 'internet', 'dados'],
    'estatistica': ['estatistica', 'dados', 'analise de dados', 'probabilidade', 'pesquisa de dados'],
    'psicologia': ['psicologia', 'comportamento', 'mente', 'emocoes', 'terapia', 'saude mental', 'neurociencia', 'relacionamento'],
    'design': ['arte', 'design', 'criacao', 'estetica', 'visual', 'grafico', 'ilustracao', 'cores', 'formatacao'],
    'administracao': ['negocios', 'gestao', 'administracao', 'empreendedorismo', 'financas', 'marketing', 'lideranca', 'empresas'],
    'literatura': ['literatura', 'leitura', 'escrita', 'historia', 'poesia', 'narrativa', 'linguistica', 'livros'],
    'danca': ['danca', 'dancarino', 'bailarina', 'coreografia', 'expressao corporal'],
    'teatro': ['teatro', 'ator', 'atriz', 'atuacao', 'producao cenica'],
    'musica': ['musica', 'cantor', 'cantora', 'cantar', 'canto', 'instrumento', 'composicao', 'som'],
    'direito': ['direito', 'leis', 'justica', 'advocacia', 'legislacao', 'crime'],
    'medicina': ['medicina', 'saude', 'pacientes', 'doencas', 'corpo humano', 'anatomia', 'clinica', 'cura'],
    'biologia': ['biologia', 'vida', 'meio ambiente', 'animais', 'plantas', 'ecologia', 'genetica', 'pesquisa biologica'],
    'engenharia': ['engenharia', 'projetos', 'construcao', 'infraestrutura', 'inovacao', 'tecnica'],
    'comunicacao': ['comunicacao', 'midia', 'jornalismo', 'publicidade', 'relacoes publicas', 'redes sociais'],
    'educacao': ['educacao', 'ensino', 'pedagogia', 'formacao', 'professor', 'escola', 'aprender'],
    'pesquisa': ['pesquisa', 'ciencia', 'descoberta', 'laboratorio', 'academicos', 'estudo'],
    'saude_coletiva': ['saude publica', 'comunidade', 'bem estar social', 'epidemiologia'],
    'gastronomia': ['culinaria', 'cozinha', 'comida', 'chef', 'alimentos'],
    'turismo': ['turismo', 'viagens', 'hoteis', 'eventos', 'cultura', 'explorar']
}

SUGGESTIONS_MAP = {
    'matematica': ['Matemática', 'Estatística', 'Atuária'],
    'fisica': ['Física', 'Engenharia Física', 'Engenharia Aeroespacial'],
    'quimica': ['Química', 'Engenharia Química', 'Farmácia', 'Bioquímica'],
    'programacao': ['Ciência da Computação', 'Análise e Desenvolvimento de Sistemas', 'Engenharia de Software', 'Sistemas de Informação'],
    'estatistica': ['Estatística', 'Ciência de Dados', 'Matemática Aplicada'],
    'psicologia': ['Psicologia', 'Psicopedagogia', 'Neuropsicologia'],
    'design': ['Design Gráfico', 'Design de Interiores', 'Design de Produto', 'Arquitetura e Urbanismo'],
    'administracao': ['Administração', 'Gestão Comercial', 'Marketing', 'Contabilidade'],
    'literatura': ['Letras', 'Produção Editorial', 'Revisão Textual'],
    'danca': ['Dança', 'Comunicação das Artes do Corpo'],
    'teatro': ['Teatro', 'Produção Cênica'],
    'musica': ['Música', 'Produção Fonográfica', 'Musicoterapia'],
    'direito': ['Direito', 'Relações Internacionais'],
    'medicina': ['Medicina', 'Enfermagem', 'Fisioterapia', 'Nutrição'],
    'biologia': ['Biologia', 'Ciências Biológicas', 'Biomedicina', 'Biotecnologia'],
    'engenharia': ['Engenharia Civil', 'Engenharia Mecânica', 'Engenharia Elétrica', 'Engenharia de Produção'],
    'comunicacao': ['Jornalismo', 'Publicidade e Propaganda', 'Relações Públicas'],
    'educacao': ['Pedagogia', 'Licenciaturas'],
    'pesquisa': ['Carreira Acadêmica', 'Pesquisador Científico'],
    'saude_coletiva': ['Saúde Coletiva', 'Gestão Hospitalar'],
    'gastronomia': ['Gastronomia', 'Hotelaria'],
    'turismo': ['Turismo', 'Gestão de Eventos']
}


AREA_SUGGESTIONS = {
    'exatas': ['Matemática', 'Física', 'Química', 'Estatística', 'Engenharias', 'Ciência da Computação'],
    'humanas': ['Direito', 'Sociologia', 'Filosofia', 'História', 'Letras', 'Psicologia', 'Serviço Social'],
    'biologicas': ['Biologia', 'Biomedicina', 'Medicina Veterinária', 'Nutrição', 'Farmácia', 'Biotecnologia'],
    'engenharias': ['Engenharia Civil', 'Engenharia Mecânica', 'Engenharia Elétrica', 'Engenharia de Produção', 'Engenharia Química', 'Engenharia de Software', 'Engenharia Aeroespacial'],
    'saude': ['Medicina', 'Enfermagem', 'Fisioterapia', 'Odontologia', 'Nutrição', 'Farmácia', 'Psicologia', 'Terapia Ocupacional'],
    'artes': ['Design Gráfico', 'Arquitetura e Urbanismo', 'Artes Visuais', 'Música', 'Teatro', 'Dança', 'Cinema e Audiovisual'],
    'negocios': ['Administração', 'Marketing', 'Gestão Financeira', 'Logística', 'Recursos Humanos', 'Economia', 'Comércio Exterior'],
    'tecnologia': ['Análise e Desenvolvimento de Sistemas', 'Engenharia de Software', 'Ciência de Dados', 'Segurança da Informação', 'Inteligência Artificial', 'Redes de Computadores', 'Sistemas de Informação'],
    'ambiental': ['Gestão Ambiental', 'Engenharia Ambiental e Sanitária', 'Agronomia', 'Oceanografia', 'Biologia Marinha'],
    'nenhuma': []
}

AREA_OPTIONS = [
    ('exatas', 'Ciências Exatas'),
    ('humanas', 'Ciências Humanas'),
    ('biologicas', 'Ciências Biológicas'),
    ('engenharias', 'Engenharia e Produção'),
    ('saude', 'Saúde e Bem-Estar'),
    ('artes', 'Artes e Design'),
    ('negocios', 'Administração e Negócios'),
    ('tecnologia', 'Tecnologia da Informação'),
    ('ambiental', 'Meio Ambiente e Agronegócios'),
    ('nenhuma', 'Nenhuma das anteriores')
]

PREFERENCE_OPTIONS = [
    ('prefere_equipes', 'Prefere trabalho em equipe'),
    ('gosta_rotina', 'Gosta de rotina e estrutura'),
    ('gosto_pessoas', 'Gosta de lidar com pessoas e interagir'),
    ('gosto_criativo', 'Prefere trabalho criativo e inovador'),
    ('gosto_externo', 'Prefere trabalho ao ar livre/campo'),
    ('gosto_ensino', 'Gosta de ensinar e compartilhar conhecimento'),
    ('gosto_analitico', 'Gosta de análise, pesquisa e resolver problemas'),
    ('gosto_lideranca', 'Prefere liderança e tomada de decisões'),
    ('gosto_tecnico', 'Gosta de aspectos técnicos e práticos'),
    ('gosto_ajudar_outros', 'Gosta de ajudar/cuidar de outras pessoas'),
    ('gosto_manual', 'Prefere trabalho manual/prático'),
    ('gosto_autonomia', 'Valoriza autonomia e independência')
]

class Perfil(Fact):
    interesses = Field(list, default=[])
    area = Field(str, default=None)
    prefere_equipes = Field(bool, default=False)
    gosta_rotina = Field(bool, default=False)
    gosto_pessoas = Field(bool, default=False)
    gosto_criativo = Field(bool, default=False)
    gosto_externo = Field(bool, default=False)
    gosto_ensino = Field(bool, default=False)
    gosto_analitico = Field(bool, default=False)
    gosto_lideranca = Field(bool, default=False)
    gosto_tecnico = Field(bool, default=False)
    gosto_ajudar_outros = Field(bool, default=False)
    gosto_manual = Field(bool, default=False)
    gosto_autonomia = Field(bool, default=False)

class VocacionalEngine(KnowledgeEngine):
    @Rule(Perfil(area=MATCH.a))
    def por_area(self, a):
        if a in AREA_SUGGESTIONS and AREA_SUGGESTIONS[a]:
            for p in AREA_SUGGESTIONS[a]:
                self.declare(Fact(sugestao=p))

    @Rule(Perfil(interesses=MATCH.i))
    def por_interesses(self, i):
        for intr in i:
            if intr in SUGGESTIONS_MAP:
                for p in SUGGESTIONS_MAP[intr]:
                    self.declare(Fact(sugestao=p))

    @Rule(
        Perfil(area='tecnologia',
               prefere_equipes=True,
               gosto_criativo=True,
               gosta_rotina=True)
    )
    def ti_equipe_criativo_rotina(self):
        self.declare(Fact(sugestao='Desenvolvimento Frontend (UI/UX)'))
        self.declare(Fact(sugestao='Engenharia de Software (foco em produto)'))
        self.declare(Fact(sugestao='Analista de Sistemas/Negócios'))
        self.declare(Fact(sugestao='Arquiteto de Soluções'))

    @Rule(
        Perfil(area='tecnologia',
               prefere_equipes=True,
               gosto_analitico=True)
    )
    def ti_equipe_analitico(self):
        self.declare(Fact(sugestao='Cientista de Dados'))
        self.declare(Fact(sugestao='Engenheiro de Dados'))
        self.declare(Fact(sugestao='Engenheiro de Machine Learning'))
        self.declare(Fact(sugestao='Analista de Cibersegurança'))

    @Rule(
        Perfil(area='tecnologia',
               gosta_rotina=True,
               gosto_tecnico=True)
    )
    def ti_rotina_tecnico(self):
        self.declare(Fact(sugestao='Administrador de Banco de Dados (DBA)'))
        self.declare(Fact(sugestao='Administrador de Redes'))
        self.declare(Fact(sugestao='Suporte Técnico de TI'))
        self.declare(Fact(sugestao='Desenvolvedor Backend (sistemas com alta demanda de rotina e otimização)'))

    @Rule(
        Perfil(area='artes',
               gosto_criativo=True,
               gosto_autonomia=True)
    )
    def artes_criativo_autonomia(self):
        self.declare(Fact(sugestao='Designer Freelancer'))
        self.declare(Fact(sugestao='Artista Plástico'))
        self.declare(Fact(sugestao='Ilustrador'))
        self.declare(Fact(sugestao='Escritor/Autor'))


    @Rule(Perfil(gosto_ajudar_outros=True))
    def preferencia_ajudar(self):
        self.declare(Fact(sugestao='Psicólogo'))
        self.declare(Fact(sugestao='Assistente Social'))
        self.declare(Fact(sugestao='Enfermeiro'))
        self.declare(Fact(sugestao='Médico'))

    @Rule(Perfil(gosto_criativo=True, area=OR('artes', 'comunicacao', 'tecnologia', None)))
    def preferencia_criatividade(self):
        self.declare(Fact(sugestao='Designer Gráfico'))
        self.declare(Fact(sugestao='Arquiteto'))
        self.declare(Fact(sugestao='Publicitário'))
        self.declare(Fact(sugestao='Desenvolvedor de Jogos'))

    @Rule(Perfil(gosto_analitico=True, area=OR('exatas', 'tecnologia', 'engenharias', None)))
    def preferencia_analise(self):
        self.declare(Fact(sugestao='Cientista de Dados'))
        self.declare(Fact(sugestao='Analista Financeiro'))
        self.declare(Fact(sugestao='Engenheiro de Pesquisa e Desenvolvimento'))
        self.declare(Fact(sugestao='Atuário'))

    @Rule(Perfil(gosto_lideranca=True, area=OR('negocios', 'engenharias', 'saude', None)))
    def preferencia_lideranca(self):
        self.declare(Fact(sugestao='Administrador (Gerência)'))
        self.declare(Fact(sugestao='Diretor de Projetos'))
        self.declare(Fact(sugestao='Gestor de Equipes'))

    @Rule(Perfil(gosto_ensino=True))
    def preferencia_ensino(self):
        self.declare(Fact(sugestao='Professor (Ensino Básico/Superior)'))
        self.declare(Fact(sugestao='Pedagogo'))
        self.declare(Fact(sugestao='Tutor/Instrutor de Treinamentos'))

    @Rule(Perfil(gosto_externo=True, area=OR('ambiental', 'biologicas', None)))
    def preferencia_externo(self):
        self.declare(Fact(sugestao='Engenheiro Agrônomo'))
        self.declare(Fact(sugestao='Biólogo (Campo)'))
        self.declare(Fact(sugestao='Guia de Turismo Ecológico'))
        self.declare(Fact(sugestao='Veterinário (com atuação em campo)'))

    @Rule(Perfil(gosto_tecnico=True, area=OR('tecnologia', 'engenharias', 'exatas', None)))
    def preferencia_tecnico(self):
        self.declare(Fact(sugestao='Técnico em Eletrônica'))
        self.declare(Fact(sugestao='Engenheiro de Manutenção'))
        self.declare(Fact(sugestao='Especialista em Redes'))

    @Rule(Perfil(gosto_pessoas=True, area=OR('humanas', 'saude', 'negocios', 'comunicacao', None)))
    def preferencia_pessoas(self):
        self.declare(Fact(sugestao='Recursos Humanos'))
        self.declare(Fact(sugestao='Psicólogo Organizacional'))
        self.declare(Fact(sugestao='Vendedor/Consultor de Vendas'))
        self.declare(Fact(sugestao='Jornalista (Entrevistas)'))

    @Rule(Perfil(prefere_equipes=True, area=OR('tecnologia', 'engenharias', 'saude', 'negocios', None)))
    def preferencia_equipes(self):
        self.declare(Fact(sugestao='Gerente de Projetos'))
        self.declare(Fact(sugestao='Desenvolvedor de Software'))
        self.declare(Fact(sugestao='Profissional de Marketing Digital (equipes)'))

    @Rule(Perfil(gosta_rotina=True, area=OR('negocios', 'tecnologia', 'exatas', None)))
    def preferencia_rotina(self):
        self.declare(Fact(sugestao='Analista Financeiro (Rotinas de Balanço)'))
        self.declare(Fact(sugestao='Contador'))
        self.declare(Fact(sugestao='Administrativo/Escritório'))
        self.declare(Fact(sugestao='Analista de Testes (QA)'))


    @Rule(
        Perfil(area=None, interesses=MATCH.i)
    )
    def explorar_interesses_sem_area(self, i):
        if not i:
            self.declare(Fact(sugestao='Explorar áreas variadas (faça testes vocacionais mais aprofundados)'))

    @Rule(
        Perfil(area=None, interesses=[])
    )
    def exploracao_geral(self):
        self.declare(Fact(sugestao='Explore seus interesses e talentos através de atividades extracurriculares ou voluntariado.'))
        self.declare(Fact(sugestao='Considere buscar um orientador vocacional para um acompanhamento personalizado.'))
        self.declare(Fact(sugestao='Pesquise sobre as diversas áreas do conhecimento para descobrir o que mais te atrai.'))


def normalize_interests(raw_list):
    normalized = []
    for phrase in raw_list:
        pl = phrase.lower().strip()
        if not pl: continue
        matched = False
        for key, syns in SYNONYMS_MAP.items():
            for syn in syns:
                if syn in pl:
                    if key not in normalized:
                        normalized.append(key)
                    matched = True
                    break
            if matched:
                break
        if not matched and pl:
            normalized.append(pl)
    return normalized

TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><title>Orientação Vocacional com IA</title>
<style>
  body{background:#121212;color:#e0e0e0;font-family:Arial,sans-serif;margin:0;padding:0}
  .c{max-width:800px;margin:2rem auto;padding:1rem;background:#1e1e1e;border-radius:8px;box-shadow:0 4px 8px rgba(0,0,0,.2);}
  h1{text-align:center;margin-bottom:1.5rem;color:#bb86fc; font-weight: bold;}
  form{display:flex;flex-direction:column;gap:1.5rem;}
  .fg{display:flex;flex-direction:column;}
  label{margin-bottom:.5rem;color:#e0e0e0;}
  .label-bold {font-weight: bold;} /* Nova classe para negrito apenas em labels específicas */
  input[type=text],select{background:#2a2a2a;border:1px solid #444;color:#e0e0e0;padding:.6rem;border-radius:4px;width:100%;box-sizing:border-box;}
  input[type=text]:focus,select:focus{outline:none;border-color:#bb86fc;}
  .rg,.cg{display:flex;flex-wrap:wrap;gap:1rem;}
  .rg label,.cg label{display:flex;align-items:center;gap:.4rem;cursor:pointer;}
  input[type=radio],input[type=checkbox]{accent-color:#bb86fc;}
  button{background:#bb86fc;color:#121212;border:none;padding:.9rem 1.5rem;border-radius:4px;cursor:pointer;font-size:1.1rem;font-weight:bold;transition:background .3s ease;}
  button:hover{background:#aa75e8;}
  #res{background:#2a2a2a;border:1px solid #444;border-radius:4px;padding:1.5rem;min-height:180px;margin-top:2rem;white-space:pre-wrap;line-height:1.6;color:#ccc;}
  #res h2 {color:#bb86fc; margin-top:0; border-bottom:1px solid #444; padding-bottom:0.5rem; margin-bottom:1rem; font-weight: bold;}
  #res ul {list-style:none; padding:0;}
  #res ul li {margin-bottom:0.5rem; display:flex; align-items:flex-start;}
  #res ul li:before {content:'\\2022'; color:#bb86fc; margin-right:0.8rem; font-size:1.2em; line-height:1;}
</style>
</head>
<body>
<div class="c">
  <h1>Sistema de Orientação Vocacional</h1>
  <form method="post">
    <div class="fg"><label for="interesses" class="label-bold">Seus principais interesses (separados por vírgula):</label><input type="text" name="interesses" id="interesses" placeholder="Ex: programação, psicologia, arte, dados"></div>
    <div class="fg"><label class="label-bold">Qual área do conhecimento você se identifica mais?</label><div class="rg">
      {% for v,l in areas %}<label><input type="radio" name="area" value="{{v}}"{% if loop.first %} checked{% endif %}> {{l}}</label>{% endfor %}
    </div></div>
    <div class="fg"><label class="label-bold">Marque as preferências que descrevem seu ambiente de trabalho ideal:</label><div class="cg">
      {% for k,l in prefs %}<label><input type="checkbox" name="{{k}}"> {{l}}</label>{% endfor %}
    </div></div>
    <button type="submit">Gerar Sugestões de Carreira</button>
  </form>
  <div id="res">
    {% if sugestões %}
      <h2>Suas Sugestões:</h2>
      <ul>
      {% for s in sugestões %}<li>{{s}}</li>
      {% endfor %}
      </ul>
    {% else %}
      <p>Preencha os campos acima para receber sugestões personalizadas de carreira.</p>
    {% endif %}
  </div>
</div>
</body>
</html>
'''

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    sugestões = []
    if request.method == 'POST':
        interesses = request.form.get('interesses','').split(',')
        ints = normalize_interests(interesses) if interesses else [] 
        
        area = request.form.get('area')
        if area == 'nenhuma': area = None
        
        prefs = {}
        for k,_ in PREFERENCE_OPTIONS:
            prefs[k] = bool(request.form.get(k))

        engine = VocacionalEngine()
        engine.reset()
        engine.declare(Perfil(interesses=ints, area=area, **prefs))
        engine.run()
        
        sugestões = sorted(list({f['sugestao'] for f in engine.facts.values() if 'sugestao' in f}))
        
        if not sugestões:
            sugestões.append('Não foi possível gerar sugestões específicas com base nas informações fornecidas. Tente ser mais detalhado nos interesses ou considere consultar um orientador vocacional.')

    return render_template_string(TEMPLATE, areas=AREA_OPTIONS, prefs=PREFERENCE_OPTIONS, sugestões=sugestões)

if __name__ == '__main__':
    app.run(debug=True)