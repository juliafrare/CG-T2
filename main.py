import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import glm
import math
from PIL import Image

#inicializando janela
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE);
altura = 1600
largura = 1200
window = glfw.create_window(largura, altura, "Trabalho 2", None, None)
glfw.make_context_current(window)

#vertex shader
vertex_code = """
        attribute vec3 position;
        attribute vec2 texture_coord;
        varying vec2 out_texture;
                
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;        
        
        void main(){
            gl_Position = projection * view * model * vec4(position,1.0);
            out_texture = vec2(texture_coord);
        }
        """

#fragment shader
fragment_code = """
        uniform vec4 color;
        varying vec2 out_texture;
        uniform sampler2D samplerTexture;
        
        void main(){
            vec4 texture = texture2D(samplerTexture, out_texture);
            gl_FragColor = texture;
        }
        """

# Request a program and shader slots from GPU
program  = glCreateProgram()
vertex   = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)

# Set shaders source
glShaderSource(vertex, vertex_code)
glShaderSource(fragment, fragment_code)

# Compile shaders
glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(vertex).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Vertex Shader")

glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(fragment).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Fragment Shader")

# Attach shader objects to the program
glAttachShader(program, vertex)
glAttachShader(program, fragment)

# Build program
glLinkProgram(program)
if not glGetProgramiv(program, GL_LINK_STATUS):
    print(glGetProgramInfoLog(program))
    raise RuntimeError('Linking error')
    
# Make program the default program
glUseProgram(program)

#load model from file
def load_model_from_file(filename):
    """Loads a Wavefront OBJ file. """
    objects = {}
    vertices = []
    texture_coords = []
    faces = []

    material = None

    # abre o arquivo obj para leitura
    for line in open(filename, "r"): ## para cada linha do arquivo .obj
        if line.startswith('#'): continue ## ignora comentarios
        values = line.split() # quebra a linha por espaço
        if not values: continue


        ### recuperando vertices
        if values[0] == 'v':
            vertices.append(values[1:4])


        ### recuperando coordenadas de textura
        elif values[0] == 'vt':
            texture_coords.append(values[1:3])

        ### recuperando faces 
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
        elif values[0] == 'f':
            face = []
            face_texture = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                if len(w) >= 2 and len(w[1]) > 0:
                    face_texture.append(int(w[1]))
                else:
                    face_texture.append(0)

            faces.append((face, face_texture, material))

    model = {}
    model['vertices'] = vertices
    model['texture'] = texture_coords
    model['faces'] = faces

    return model

glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
glEnable( GL_BLEND )
glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
glEnable(GL_LINE_SMOOTH)
glEnable(GL_TEXTURE_2D)
qtd_texturas = 11
textures = glGenTextures(qtd_texturas)

#load texture from file
def load_texture_from_file(texture_id, img_textura):
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    img = Image.open(img_textura)
    print(img_textura,img.mode)
    img_width = img.size[0]
    img_height = img.size[1]
    #image_data = img.tobytes("raw", "RGB", 0, -1)
    image_data = img.convert("RGBA").tobytes("raw", "RGBA",0,-1)

    #image_data = np.array(list(img.getdata()), np.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

vertices_list = []    
textures_coord_list = []

##########################
#####CARREGANDO OS MODELOS
##########################
textures_loaded = 0

def load_model(model_path, texture_path, textures_loaded):
    modelo = load_model_from_file(model_path)

    ### inserindo vertices do modelo no vetor de vertices
    print('Processando modelo ' + model_path + '. Vertice inicial:',len(vertices_list))
    faces_visited = []
    for face in modelo['faces']:
        if face[2] not in faces_visited:
            print(str(face[2]) + ' vertice inicial: ' + str(len(vertices_list)))
            faces_visited.append(face[2])
        for vertice_id in face[0]:
            vertices_list.append( modelo['vertices'][vertice_id-1] )
        for texture_id in face[1]:
            textures_coord_list.append( modelo['texture'][texture_id-1] )
    print('Processando modelo ' + model_path + '. Vertice final:',len(vertices_list))

    ### inserindo coordenadas de textura do modelo no vetor de texturas

    ### carregando textura equivalente e definindo um id (buffer): use um id por textura!
    load_texture_from_file(textures_loaded, texture_path)
    textures_loaded += 1
    return textures_loaded

#1 - terreno
textures_loaded = load_model('objects/terreno/terreno.obj', 'objects/terreno/grass-texture.png', textures_loaded)

#2 - ceu
textures_loaded = load_model('objects/ceu/sky.obj', 'objects/ceu/cloudy.png', textures_loaded)

#3 - caixa
textures_loaded = load_model('objects/caixa/crate.obj', 'objects/caixa/WoodenCrate_Crate_BaseColor.png', textures_loaded)

#4 - casa
textures_loaded = load_model('objects/casa/farmhouse.obj', 'objects/casa/FarmhouseTexture.jpg', textures_loaded)

#5 - personagem
textures_loaded = load_model('objects/personagem/anime_character.obj', 'objects/personagem/textures.png', textures_loaded)

#6 - mesa
textures_loaded = load_model('objects/mesa/table.obj', 'objects/mesa/round_table_texture.png', textures_loaded)

#7 - pet
textures_loaded = load_model('objects/pet/penguin.obj', 'objects/pet/PenguinDiffuseColor.png', textures_loaded)

#8 - carro
textures_loaded = load_model('objects/carro/car.obj', 'objects/carro/CarTexture1.png', textures_loaded)

#9 - ufo
textures_loaded = load_model('objects/ufo/ufo.obj', 'objects/ufo/UFO_color.jpg', textures_loaded)

load_texture_from_file(textures_loaded, 'objects/terreno/dirt_ground_texture.jpg')
textures_loaded += 1

################################
# Request a buffer slot from GPU
buffer = glGenBuffers(2)

vertices = np.zeros(len(vertices_list), [("position", np.float32, 3)])
vertices['position'] = vertices_list


# Upload data
glBindBuffer(GL_ARRAY_BUFFER, buffer[0])
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
stride = vertices.strides[0]
offset = ctypes.c_void_p(0)
loc_vertices = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc_vertices)
glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)

#enviando texturas p/ gpu
textures = np.zeros(len(textures_coord_list), [("position", np.float32, 2)]) # duas coordenadas
textures['position'] = textures_coord_list

# Upload data
glBindBuffer(GL_ARRAY_BUFFER, buffer[1])
glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)
stride = textures.strides[0]
offset = ctypes.c_void_p(0)
loc_texture_coord = glGetAttribLocation(program, "texture_coord")
glEnableVertexAttribArray(loc_texture_coord)
glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)

##########################
#####DESENHANDO OS OBJETOS
##########################
def desenha_terreno(top):
    
    
    # aplica a matriz model
    
    # rotacao
    angle = 0.0
    r_x = 0.0; r_y = 0.0; r_z = 1.0
    
    # translacao
    if top == 0:
        t_x = 0.0; t_y = -0.0001; t_z = 0.0
    else:
        t_x = 0.0; t_y = 50.0; t_z = 0.0
    
    # escala
    s_x = 100.0; s_y = 1.0; s_z = 100.0
    
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
       
    if top == 0:
        #define id da textura do modelo
        glBindTexture(GL_TEXTURE_2D, 0)
        # desenha o modelo
        glDrawArrays(GL_TRIANGLES, 0, 6) ## renderizando

        #define id da textura do modelo
        glBindTexture(GL_TEXTURE_2D, 9)
        # desenha o modelo
        glDrawArrays(GL_TRIANGLES, 6, 12-6) ## renderizando
    else:
        #define id da textura do modelo
        glBindTexture(GL_TEXTURE_2D, 1)
        # desenha o modelo
        glDrawArrays(GL_TRIANGLES, 0, 12) ## renderizando

def desenha_ceu(angulo_ceu):
    # aplica a matriz model
    
    # rotacao
    angle = angulo_ceu
    r_x = 0.0; r_y = 1.0; r_z = 0.0
    
    # translacao
    t_x = 0.0; t_y = 0.0; t_z = -100.0
    
    # escala
    s_x = 100.0; s_y = 100.0; s_z = 0.0
    
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
       
    #define id da textura do modelo
    glBindTexture(GL_TEXTURE_2D, 1)
    
    
    # desenha o modelo
    glDrawArrays(GL_TRIANGLES, 12, 18-12) ## renderizando

def desenha_caixa():
    # aplica a matriz model
    
    # rotacao
    angle = 0.0
    r_x = 0.0; r_y = 0.0; r_z = 1.0
    
    # translacao
    t_x = 5.0; t_y = 0.0; t_z = -40.0
    
    # escala
    s_x = 1.0; s_y = 1.0; s_z = 1.0
    
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
       
    #define id da textura do modelo
    glBindTexture(GL_TEXTURE_2D, 2)
    
    
    # desenha o modelo
    glDrawArrays(GL_TRIANGLES, 18, 1782-18) ## renderizando

def desenha_casa():
    # aplica a matriz model
    
    # rotacao
    angle = 180.0
    r_x = 0.0; r_y = 1.0; r_z = 0.0
    
    # translacao
    t_x = 10.0; t_y = 0.0; t_z = 60.0
    
    # escala
    s_x = 1.0; s_y = 1.0; s_z = 1.0
    
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
       
    #define id da textura do modelo
    glBindTexture(GL_TEXTURE_2D, 3)
    
    
    # desenha o modelo
    glDrawArrays(GL_TRIANGLES, 1782, 2784-1782) ## renderizando

def desenha_personagem():
    # aplica a matriz model
    
    # rotacao
    angle = 0.0
    r_x = 0.0; r_y = 1.0; r_z = 0.0
    
    # translacao
    t_x = -10.0; t_y = 1.0; t_z = -80.0
    
    # escala
    s_x = 1.0; s_y = 1.0; s_z = 1.0
    
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
       
    #define id da textura do modelo
    glBindTexture(GL_TEXTURE_2D, 4)
    
    
    # desenha o modelo
    glDrawArrays(GL_TRIANGLES, 2784, 24114-2784) ## renderizando

def desenha_mesa():
    # aplica a matriz model
    
    # rotacao
    angle = 0.0
    r_x = 0.0; r_y = 1.0; r_z = 0.0
    
    # translacao
    t_x = -10.0; t_y = 1.0; t_z = -75.0
    
    # escala
    s_x = 1.0; s_y = 2.0; s_z = 1.0
    
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
       
    #define id da textura do modelo
    glBindTexture(GL_TEXTURE_2D, 5)
    
    
    # desenha o modelo
    glDrawArrays(GL_TRIANGLES, 24114, 134202-24114) ## renderizando

def desenha_pet():
    # aplica a matriz model
    
    # rotacao
    angle = 0.0
    r_x = 0.0; r_y = 1.0; r_z = 0.0
    
    # translacao
    t_x = -7.0; t_y = 1.0; t_z = -77.0
    
    # escala
    s_x = 2.0; s_y = 2.0; s_z = 2.0
    
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
       
    #define id da textura do modelo
    glBindTexture(GL_TEXTURE_2D, 6)
    
    
    # desenha o modelo
    glDrawArrays(GL_TRIANGLES, 134202, 164610-134202) ## renderizando

altura_carro = 0.0
up = True

def desenha_carro(altura_carro):
    # aplica a matriz model
    
    # rotacao
    angle = 0.0
    r_x = 0.0; r_y = 1.0; r_z = 0.0
    
    # translacao
    t_x = 13.0; t_y = altura_carro; t_z = -50.0
    
    # escala
    s_x = 5.0; s_y = 5.0; s_z = 5.0
    
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
       
    #define id da textura do modelo
    glBindTexture(GL_TEXTURE_2D, 7)
    
    
    # desenha o modelo
    glDrawArrays(GL_TRIANGLES, 164610, 176004-164610) ## renderizando

def desenha_ufo():
    # aplica a matriz model
    
    # rotacao
    angle = 0.0
    r_x = 0.0; r_y = 1.0; r_z = 0.0
    
    # translacao
    t_x = 13.0; t_y = 25.0; t_z = -50.0
    
    # escala
    s_x = 5.0; s_y = 5.0; s_z = 5.0
    
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
       
    #define id da textura do modelo
    glBindTexture(GL_TEXTURE_2D, 8)  
    
    # desenha o modelo
    glDrawArrays(GL_TRIANGLES, 176004, 258816-176004) ## renderizando

    #glBindTexture(GL_TEXTURE_2D, 9)
    # desenha o modelo
    #glDrawArrays(GL_TRIANGLES, 236604, 259536-236604)

#############################
######EVENTOS CAMERA
#############################
cameraPos   = glm.vec3(-1.0,  1.0,  -5.0)
cameraFront = glm.vec3(0.0,  0.0, -1.0)
cameraUp    = glm.vec3(0.0,  1.0,  0.0)

minPos_x = -100.0
maxPos_x = 100.0
minPos_y = 0.0
maxPos_y = 50.0
minPos_z = -100.0
maxPos_z = 100.0

polygonal_mode = False

def key_event(window,key,scancode,action,mods):
    global cameraPos, cameraFront, cameraUp, polygonal_mode

    if cameraPos[0] < minPos_x:
        cameraPos[0] = -99.9
    if cameraPos[1] < minPos_y:
        cameraPos[1] = 0.1
    if cameraPos[2] < minPos_z:
        cameraPos[2] = -99.9

    if cameraPos[0] > maxPos_x:
        cameraPos[0] = 99.9
    if cameraPos[1] > maxPos_y:
        cameraPos[1] = 49.9
    if cameraPos[2] > maxPos_z:
        cameraPos[2] = 99.9
    
    cameraSpeed = 0.2
    if key == 87 and (action==1 or action==2): # tecla W
        cameraPos += cameraSpeed * cameraFront
    
    if key == 83 and (action==1 or action==2): # tecla S
        cameraPos -= cameraSpeed * cameraFront
    
    if key == 65 and (action==1 or action==2): # tecla A
        cameraPos -= glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed
        
    if key == 68 and (action==1 or action==2): # tecla D
        cameraPos += glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed
        
    if key == 80 and action==1 and polygonal_mode==True:
        polygonal_mode=False
    else:
        if key == 80 and action==1 and polygonal_mode==False:
            polygonal_mode=True
        
        
        
firstMouse = True
yaw = -90.0 
pitch = 0.0
lastX =  largura/2
lastY =  altura/2

def mouse_event(window, xpos, ypos):
    global firstMouse, cameraFront, yaw, pitch, lastX, lastY
    if firstMouse:
        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX = xpos
    lastY = ypos

    sensitivity = 0.3 
    xoffset *= sensitivity
    yoffset *= sensitivity

    yaw += xoffset;
    pitch += yoffset;

    
    if pitch >= 90.0: pitch = 90.0
    if pitch <= -90.0: pitch = -90.0

    front = glm.vec3()
    front.x = math.cos(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    front.y = math.sin(glm.radians(pitch))
    front.z = math.sin(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    cameraFront = glm.normalize(front)


    
glfw.set_key_callback(window,key_event)
glfw.set_cursor_pos_callback(window, mouse_event)


#matrizes model, view e projection
def model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z):
    
    angle = math.radians(angle)
    
    matrix_transform = glm.mat4(1.0) # instanciando uma matriz identidade
    
    # aplicando rotacao
    matrix_transform = glm.rotate(matrix_transform, angle, glm.vec3(r_x, r_y, r_z))
        
  
    # aplicando translacao
    matrix_transform = glm.translate(matrix_transform, glm.vec3(t_x, t_y, t_z))    
    
    # aplicando escala
    matrix_transform = glm.scale(matrix_transform, glm.vec3(s_x, s_y, s_z))
    
    matrix_transform = np.array(matrix_transform).T # pegando a transposta da matriz (glm trabalha com ela invertida)
    
    return matrix_transform

def view():
    global cameraPos, cameraFront, cameraUp
    mat_view = glm.lookAt(cameraPos, cameraPos + cameraFront, cameraUp)
    mat_view = np.array(mat_view)
    return mat_view

def projection():
    global altura, largura
    # perspective parameters: fovy, aspect, near, far
    mat_projection = glm.perspective(glm.radians(45.0), largura/altura, 0.1, 1000.0)
    mat_projection = np.array(mat_projection)    
    return mat_projection

#exibindo a janela
glfw.show_window(window)
glfw.set_cursor_pos(window, lastX, lastY)

#loop da janela
glEnable(GL_DEPTH_TEST) ### importante para 3D

while not glfw.window_should_close(window):

    glfw.poll_events() 
    
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glClearColor(1.0, 1.0, 1.0, 1.0)
    
    if polygonal_mode==True:
        glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
    if polygonal_mode==False:
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
    
    if altura_carro < 10.0 and up == True:
        altura_carro += 0.01
    elif altura_carro > 0.0 and up == False:
        altura_carro -= 0.01
    elif altura_carro >= 10.0:
        up = False
    elif altura_carro <= 0.0:
        up = True

    #desenhar objetos
    desenha_terreno(0)
    desenha_terreno(1)
    desenha_ceu(0)
    desenha_ceu(90)
    desenha_ceu(180)
    desenha_ceu(270)
    desenha_caixa()
    desenha_casa()
    desenha_personagem()
    desenha_mesa()
    desenha_pet()
    desenha_carro(altura_carro)
    desenha_ufo()

    mat_view = view()
    loc_view = glGetUniformLocation(program, "view")
    glUniformMatrix4fv(loc_view, 1, GL_FALSE, mat_view)

    mat_projection = projection()
    loc_projection = glGetUniformLocation(program, "projection")
    glUniformMatrix4fv(loc_projection, 1, GL_FALSE, mat_projection)    
    
    glfw.swap_buffers(window)

glfw.terminate()
