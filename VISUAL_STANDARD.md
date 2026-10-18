# VISUAL STANDARD

## Objetivo visual
O padrao visual da OpenBlast neste projeto e de luxo discreto, tecnico e contido. A interface deve transmitir precisao operacional, confianca e clareza, sem parecer publicitaria, pesada ou chamativa.

## Intencao estetica
- Base visual clara, limpa e silenciosa.
- Predominio de branco e off-white.
- Contraste controlado, sem excesso de preto absoluto.
- Geometria mais quadrada do que organica.
- Destaques visuais pequenos, nunca espalhafatosos.
- Identidade com cara de produto tecnico premium, nao de landing page promocional.

## Referencia aplicada à home (layout "Dashboards", revisão 2026-10-18)
- Container central de 1180px, fundo branco, Arial/Helvetica.
- Barra superior: logo OpenBlast pequeno (altura 40px) + wordmark "Open" grafite / "Blast" vermelho à esquerda. No hub US Vale Verde, logo Enaex Brasil à direita (`usvaleverde/assets/enaex-brasil.png`, cópia redimensionada de `VISUAL/Enaex Brasil.png`); o hub público não usa logo Enaex.
- Título "FERRAMENTAS" em vermelho `#B5121B`, caixa alta, peso regular, 36px. Subtítulo em uma linha, cinza `#4a4f55`.
- Controles: rótulo pequeno cinza `#8a8f96` ("Buscar ferramenta", "Grupo") acima de campo com borda fina `#c4c7cb` (busca com 42px de altura, largura total); contagem "N de N ferramentas" à direita, pequena, cinza.
- Títulos de seção: texto regular grafite 20px com filete `#e3e3e3` logo abaixo.
- Cards em grade de 4 colunas (2 em tablet, 1 em mobile): borda fina `#e3e3e3`, fundo branco, sem sombra. Ícone no canto superior esquerdo, título em negrito grafite, status em cinza só quando o manifesto marca `status_indicator: false` (ex.: "Em desenvolvimento"). Hover: a borda passa para rosa suave `#e3b5b8`.
- Ícones: pictogramas de traço fino (1.3px, `vector-effect: non-scaling-stroke`) dentro de um hexágono de contorno fino (48x42px). Vermelho `#B5121B` para ferramentas ativas; cinza `#8a8f96` para ferramentas em desenvolvimento.
- Nao ha tooltip flutuante; a descricao completa fica disponivel apenas para leitores de tela (`sr-only`) e para a busca.
- Rodapé: filete grafite fino, texto pequeno cinza, em caixa normal (esquerda: "Hub operacional OpenBlast"; direita: "US Vale Verde" ou "Hub público").
- Paleta da home: vermelho `#B5121B`, grafite `#3d4148`, cinza médio `#8a8f96`, cinza claro `#c4c7cb`, rosa suave `#e3b5b8` (uso de apoio), linha `#e3e3e3`, texto secundário `#4a4f55`. O vermelho de acento `#E20613` fica restrito ao contorno de foco.
- Nao usar Google Fonts na home: a fonte é o stack do sistema (Arial/Helvetica).

## Principios obrigatorios
- Usar referencias OpenBlast. Excecao documentada: o logo Enaex Brasil aparece somente no hub US Vale Verde (pedido explicito de 2026-10-18), nunca no hub publico.
- Manter uma unica presenca principal do logo por tela.
- O logo deve ser pequeno e secundario em relacao ao conteudo.
- O conteudo funcional deve dominar a interface, nao a marca.
- Preferir sobriedade a impacto visual.

## Paleta
- Fundo principal: branco puro ou quase branco.
- Fundos secundarios: branco quente ou cinza muito claro.
- Linhas: cinza suave, de baixa agressividade.
- Texto principal: quase preto, sem contraste brutal.
- Texto secundario: cinza quente ou cinza frio suave.
- Cinza de identidade: Cinza Enaex `#38424B`.
- Acento principal: Vermelho Enaex `#E20613`.

## Tipografia
- Titulos: fortes, compactos e tecnicos.
- Corpo: limpo, neutro e muito legivel.
- Labels e overlines: discretos, com caixa alta e espacamento controlado.
- Evitar tipografia rebuscada, decorativa ou com personalidade excessiva.

## Logo e branding
- O logo deve aparecer uma vez por pagina, normalmente no topo.
- No hub de ferramentas, o cabeçalho fica sobre fundo branco, com logo pequeno acima do título e um filete cinza-claro separando-o do conteúdo (ver "Referencia aplicada à home").
- Nao duplicar logo no hero e no header ao mesmo tempo.
- Tamanho alvo no desktop:
  - Hub: entre 24px e 32px de largura.
  - Ferramentas: entre 22px e 48px de largura, priorizando o menor valor que preserve legibilidade.
- Tamanho alvo no mobile:
  - entre 20px e 32px.
- Nao usar sombras fortes no logo.
- Nao transformar o logo em elemento protagonista.

## Layout e espacamento
- Muito respiro.
- Blocos bem alinhados e previsiveis.
- Cards com leitura limpa e densidade moderada.
- Radius pequeno:
  - preferencia entre 4px e 8px.
- Evitar formas muito arredondadas, bolhas, orbs ou glassmorphism.
- Evitar composicoes com excesso de camadas e efeitos.

## Fundos e textura
- Fundo base claro.
- Pode usar grade sutil quadrada como textura de apoio.
- A textura deve quase desaparecer quando nao observada de perto.
- Nao usar fundos escuros como linguagem primaria.
- Nao usar gradientes chamativos ou atmosfericos.

## Componentes
- Cards com borda fina e sombra muito leve.
- Hover com deslocamento minimo, em geral 1px.
- Botoes com hierarquia clara:
  - primario com acento OpenBlast,
  - secundarios claros,
  - ghosts neutros.
- Chips, badges e pills devem ser pequenos e discretos.

## Movimento
- Animacao deve ser rara e funcional.
- Evitar entrada teatral, stagger exagerado, glow ou flutuacao.
- Quando houver interacao, ela deve ser curta e quase imperceptivel.

## Copy visual
- Tom objetivo, tecnico e calmo.
- Evitar frases de marketing.
- Evitar excesso de adjetivos.
- Preferir rotulos claros, sem floreio.

## Antipadroes
- Logo grande.
- Logo duplicado.
- Fundo escuro dominante.
- Radius muito alto.
- Sombras pesadas.
- Gradientes fortes.
- Roxo como cor dominante.
- Interface com cara de template genérico de SaaS.
- Hero promocional com linguagem grandiosa.

## Checklist para IA
Antes de alterar qualquer interface:
1. Verificar se a pagina ja usa branco, off-white e linhas suaves.
2. Verificar se o logo aparece apenas uma vez.
3. Reduzir o logo se ele estiver chamando mais atencao que o titulo.
4. Confirmar que os cantos estao pequenos e mais quadrados.
5. Remover efeitos visuais desnecessarios antes de adicionar novos.
6. Garantir que o acento vermelho seja pontual, nao dominante.
7. Manter o conteudo operacional como elemento principal.

## Regra de decisao
Se houver duvida entre uma opcao mais luxuosa e uma opcao mais discreta, escolher a mais discreta.
