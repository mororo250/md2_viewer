# TP 3

##### Aluno: João Marcos Mororo Costa
##### MAtricula: 2016103374

## Visão Geral

Implementação em python de programa que ler arquivo md2 e renderizada usando opengl.

## Instruções

### Parâmetros/Argumentos

Existem 4 parametro, os quais todos são opcionais. Caso não selecione nenhum deles será renderizado uma cena padrão.

1. --filepath_md2 ou -f - É o endereço do .md2 file a ser renderizado.

2. --texture ou -t - Endereço da textura a ser aplicada.

3. -skin Indice da skin que quer usar entre as fornecidas pelo arquivo.

4. --state - Estado do modelo a ser renderizado pode ser True or False caso True o estado é STATIC e apenas o primeiro frame vai ser renderizado caso contrario será DINAMIC e a animação será renderizada. Caso o MD2 file forneça apenas um frame state será igual a STATIC. 

Além dos argumentos é possível mudar a animação rodando entre essas 21: 
    STAND
    RUN
    ATTACK
    PAIN_A
    PAIN_B
    PAIN_C
    JUMP
    FLIP
    SALUTE
    FALLBACK
    WAVE
    POINT
    CROUCH_STAND
    CROUCH_WALK
    CROUCH_ATTACK
    CROUCH_PAIN
    CROUCH_DEATH
    DEATH_FALLBACK
    DEATH_FALLFORWARD
    DEATH_FALLBACKSLOW
    BOOM
    Para mudar entre as animações use seta para cima para ir para próxima da lista e seta para baixo para rodar animação anterior.


## Implementação:

### Shaders

Foi implementado shaders no programa foi usado um simples phong shader que usa a cor da textura no lugar das cores difusa e ambiente do material. Isso é um problema, pois como toda textura possui mesma cor especular alguns modelos podem parecer bem esquisitos.

Para implementação foi feito uma classe Shader que possui as seguintes funções:
    __compileShader()
    __createShader()
    bind() Deve ser chamado sempre antes de renderizar o frame.
    unbind() Não é realmente necessário, mas facilita debugar e ne algumas situações torna o codigo mas legivel.
    GetProgram() 

Deecidi colocar os arquivos .frag e .vert em um directorio: glsl.

Na implementação dos shaders foi usado glsl 1.3 o motivo disso é que nessa versão é extremamente facil de trablhar com legacy(glNormal3fv, glVertex3fv) opengl e shaders ao mesmo tempo, pois ainda possui alguns métodos como gl_Vertex, gl_Normal ou gl_MultiTexCoord0.

### Textura

Foi criado uma textura branca 1 x 1 para caso nenhuma textura seja fornecida. O unico formato legivel pelo programa é o .pcx. Tinha planejado que funcionasse com .bmp e .tga também, mas devido a alguns bugs e a falta de tempo não foi implementados loaders para esses formatos.

### Md2 Loader.

Foi usado uma serie de classes para guardar a informação do arquivo md2:
    md2_anim - guarda o frame sendo renderizado assim como seus limites(primeiro e ultimo frame)
    md2_texCoord - guarda cordenadas da textura
    md2_triangle - informação do triangulo.
    md2_vertex - informação do vertex.
    md2_frame - informação do frame.
    md2_header - informação do header.
    
Como varias dessas classes possuem valores imutaveis foi utilizado do NamedTuple design para implementar alguma delas. Essa forma de implementar deixa o programa mais legivel e bastante limpo.
    
###### MD2_model class
Classe responsável por gerenciar informação do arquivo md2.
Possui as seguintes funções:

load_texture - recebe o endereço da textura e carrega ela.
load_skin - usada quando se planeja usar skin fornecida por md2 recebi o indice como parametro. Também é usada caso não seja fornecida nenhuma texture atravez do argumento --texture, pois caso nenhuma texture seja fornecida o programa testa se algumas dos endereços fornecido por skins no arquivo md2 existem, caso exista carrega textura, caso não exista usa textura branca padrão.
animate - decidi frame a ser renderizado.
interpolate - responsável pela interpolação. Faz interpolação linear entre o frame atual e o próximo frame a ser renderizado.
change_animation - muda entre os 21 MD2 modelos de animação.

## Referencia:

http://tfc.duke.free.fr/old/models/md2.htm
https://github.com/assimp/assimp
