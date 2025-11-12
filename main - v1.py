import pygame
import random
import math

pygame.init()
pygame.font.init() # Garantir que o módulo de fontes esteja inicializado

# === CONSTANTES ===
WIDTH, HEIGHT = 800, 600
FPS = 60

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 168, 82)
RED = (200, 0, 0)
DARK_RED = (100, 0, 0)
SKIN = (255, 220, 200)
PURPLE = (138, 43, 226)
BLUE = (0, 100, 255)
GRAY = (180, 180, 180)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Configurações do Jogo
VAMPIRE_START_HP = 100 # Vampiro agora tem HP
VAMPIRE_SPEED = 5
PROJECTILE_SPEED = 10
BASE_SHOOT_COOLDOWN = 1000  # ms
MIN_SHOOT_COOLDOWN = 150    # ms
COOLDOWN_REDUCTION_PER_STRENGTH = 30

ENEMY_BASE_SPEED = 1.5
ENEMY_SPEED_INCREMENT_PER_STAGE = 0.1
BASE_HUMANS_PER_STAGE = 3
HUMANS_INCREMENT_PER_STAGE = 1
BASE_ENEMIES_PER_STAGE = 2
ENEMIES_INCREMENT_PER_STAGE = 1

EXP_PER_HUMAN = 15
EXP_PER_ENEMY = 10
EXP_TO_LEVEL_UP_BASE = 20

# Níveis para habilidades
SPREAD_SHOT_LEVEL = 5
BURST_SHOT_LEVEL = 10 # Tiro em 360

# Fontes
FONT_SMALL = pygame.font.SysFont("arial", 20)
FONT_MEDIUM = pygame.font.SysFont("arial", 30)
FONT_LARGE = pygame.font.SysFont("arial", 40)

# === ASSETS GLOBAIS (SPRITES PRÉ-RENDERIZADOS) ===
SPRITES = {}

def create_sprites():
    # Vampiro
    v_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.ellipse(v_surface, SKIN, (10, 0, 20, 20)) # Cabeça
    pygame.draw.rect(v_surface, DARK_RED, (5, 20, 30, 20)) # Corpo
    pygame.draw.polygon(v_surface, BLACK, [(5, 20), (35, 20), (20, 35)]) # Capa
    SPRITES['vampire'] = v_surface

    # Humano Vivo
    h_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(h_surface, SKIN, (10, 6), 6) # Cabeça
    pygame.draw.rect(h_surface, BLUE, (4, 12, 12, 8)) # Corpo
    SPRITES['human_alive'] = h_surface

    # Humano Morto/Sugado
    hd_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.rect(hd_surface, GRAY, (2, 8, 16, 6)) # Corpo caído
    pygame.draw.circle(hd_surface, SKIN, (7, 7), 4) # Cabeça caída
    SPRITES['human_dead'] = hd_surface

    # Inimigo
    e_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.ellipse(e_surface, PURPLE, (0, 0, 30, 30))
    pygame.draw.circle(e_surface, RED, (10, 10), 4) # Olho
    pygame.draw.circle(e_surface, RED, (20, 10), 4) # Olho
    SPRITES['enemy'] = e_surface

    # Projétil
    p_surface = pygame.Surface((8, 8))
    p_surface.fill(RED)
    SPRITES['projectile'] = p_surface

    # Bomba de Sangue (projétil)
    bb_surface = pygame.Surface((15, 15), pygame.SRCALPHA)
    pygame.draw.circle(bb_surface, DARK_RED, (7, 7), 7)
    SPRITES['blood_bomb_projectile'] = bb_surface

    # Raio Noturno (projétil)
    nb_surface = pygame.Surface((50, 6), pygame.SRCALPHA) # Mais comprido
    nb_surface.fill(PURPLE)
    SPRITES['night_beam_projectile'] = nb_surface

create_sprites() # Chamar uma vez para popular SPRITES

# === CLASSES ===

class GameObject(pygame.sprite.Sprite):
    def __init__(self, image_key, pos):
        super().__init__()
        self.image_key = image_key
        self.image = SPRITES[image_key]
        self.rect = self.image.get_rect(center=pos)

class Vampire(GameObject):
    def __init__(self, pos):
        super().__init__('vampire', pos)
        self.speed = VAMPIRE_SPEED
        self.exp = 0
        self.level = 1
        self.title = "New Vampire"
        self.hp = VAMPIRE_START_HP
        self.max_hp = VAMPIRE_START_HP
        self.direction = pygame.Vector2(1, 0)
        self.vampiric_strength = 0
        self.shoot_cooldown = BASE_SHOOT_COOLDOWN
        self.last_shot_time = 0
        
        self.spells = {} # Ex: {'blood_bomb': {'unlocked': True, 'last_used': 0, 'data': SPELLS_DATA['blood_bomb']}}
        self.equipped_spell_id = None
        self.check_spell_unlocks()

    def update(self, keys, game_state):
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        if dx != 0 or dy != 0:
            self.direction = pygame.Vector2(dx, dy).normalize()
            self.rect.x += self.speed * self.direction.x
            self.rect.y += self.speed * self.direction.y
        
        # Manter dentro da tela
        self.rect.clamp_ip(screen.get_rect())
        self.update_title()
        
        # Recuperar HP no castelo
        if game_state.current_map == "castle" and self.hp < self.max_hp:
            self.hp += 0.05 # Regeneração lenta
            if self.hp > self.max_hp: self.hp = self.max_hp


    def gain_exp(self, amount):
        self.exp += amount
        exp_to_next_level = EXP_TO_LEVEL_UP_BASE * self.level
        if self.exp >= exp_to_next_level:
            self.exp -= exp_to_next_level
            self.level += 1
            self.max_hp += 10 # Aumenta HP máximo com o nível
            self.hp = self.max_hp # Cura total ao subir de nível
            print(f"Vampire leveled up to {self.level}!")
            self.check_spell_unlocks()

    def update_title(self):
        if self.level < 5: self.title = "Fledgling"
        elif self.level < 10: self.title = "Blood Seeker"
        elif self.level < SPREAD_SHOT_LEVEL * 3 : self.title = "Night Stalker"
        elif self.level < BURST_SHOT_LEVEL * 2: self.title = "Elder Vampire"
        else: self.title = "Vampire Lord"

    def increase_vampiric_strength(self, amount=1):
        self.vampiric_strength += amount
        self.shoot_cooldown = max(MIN_SHOOT_COOLDOWN, BASE_SHOOT_COOLDOWN - self.vampiric_strength * COOLDOWN_REDUCTION_PER_STRENGTH)
        print(f"Vampiric Strength: {self.vampiric_strength}, Shoot Cooldown: {self.shoot_cooldown}")

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_cooldown:
            self.last_shot_time = current_time
            projectiles_to_add = []

            if self.level >= BURST_SHOT_LEVEL: # Tiro 360
                for i in range(12): # 12 projéteis, um a cada 30 graus
                    angle = i * 30
                    dir_vec = self.direction.rotate(angle)
                    projectiles_to_add.append(Projectile(self.rect.center, dir_vec, 'projectile', 10))
            elif self.level >= SPREAD_SHOT_LEVEL: # Tiro espalhado
                projectiles_to_add.append(Projectile(self.rect.center, self.direction, 'projectile', 10))
                projectiles_to_add.append(Projectile(self.rect.center, self.direction.rotate(25), 'projectile', 10))
                projectiles_to_add.append(Projectile(self.rect.center, self.direction.rotate(-25), 'projectile', 10))
            else: # Tiro normal
                projectiles_to_add.append(Projectile(self.rect.center, self.direction, 'projectile', 10))
            
            return projectiles_to_add
        return []

    def check_spell_unlocks(self):
        for spell_id, data in SPELLS_DATA.items():
            if spell_id not in self.spells and self.level >= data['unlock_level']:
                self.spells[spell_id] = {
                    'unlocked': True, 
                    'last_used': 0, 
                    'data': data
                }
                print(f"Spell Unlocked: {data['name']}")

    def equip_spell(self, spell_id_to_equip):
        if spell_id_to_equip in self.spells and self.spells[spell_id_to_equip]['unlocked']:
            self.equipped_spell_id = spell_id_to_equip
            print(f"Equipped Spell: {self.spells[spell_id_to_equip]['data']['name']}")
        elif spell_id_to_equip is None:
             self.equipped_spell_id = None
             print("Spells unequipped")
        else:
            print(f"Cannot equip spell ID: {spell_id_to_equip}. Not unlocked or invalid.")


    def use_equipped_spell(self):
        if not self.equipped_spell_id:
            return None

        spell = self.spells[self.equipped_spell_id]
        current_time = pygame.time.get_ticks()

        if current_time - spell['last_used'] > spell['data']['cooldown']:
            spell['last_used'] = current_time
            print(f"Used spell: {spell['data']['name']}")
            # A função de ativação retorna o(s) projétil(eis) da magia ou None
            return spell['data']['activate_func'](self) 
        else:
            #print(f"Spell {spell['data']['name']} on cooldown.")
            pass
        return None
        
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            return True # Morreu
        return False # Ainda vivo

class Human(GameObject):
    def __init__(self, pos):
        super().__init__('human_alive', pos)
        self.sucked = False

    def get_sucked(self):
        if not self.sucked:
            self.sucked = True
            self.image = SPRITES['human_dead']
            # Humanos mortos não devem mais interagir ou ser alvos
            # Poderia adicionar a um grupo diferente ou apenas mudar o estado

class Enemy(GameObject):
    def __init__(self, pos, speed):
        super().__init__('enemy', pos)
        self.speed = speed

    def update(self, target_pos):
        direction = pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)
        if direction.length() > 0:
            direction = direction.normalize()
            self.rect.move_ip(direction * self.speed)

class Projectile(GameObject):
    def __init__(self, pos, direction, image_key='projectile', speed=PROJECTILE_SPEED, damage=10, lifetime=2000):
        super().__init__(image_key, pos)
        self.velocity = direction * speed
        self.damage = damage
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime # em milissegundos

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        if not screen.get_rect().contains(self.rect) or \
           pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

# --- Classes de Magias Específicas (Projéteis) ---
class BloodBombExplosion(GameObject):
    def __init__(self, pos):
        # Sprite temporário para a explosão
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ORANGE, (40, 40), 40)
        pygame.draw.circle(self.image, RED, (40, 40), 30)
        super().__init__('blood_bomb_projectile', pos) # Posição inicial é a do projétil
        self.rect = self.image.get_rect(center=pos)
        self.damage = 30 # Dano da explosão
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 300 # Duração da visualização da explosão

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill() # Remove a explosão após a duração


# === FUNÇÕES DE MAGIA ===
def activate_blood_bomb(caster):
    # Cria um projétil de bomba que explode ao atingir o limite ou após um tempo
    # Por simplicidade, vamos fazer explodir perto do vampiro na direção que ele olha
    bomb_target_pos = pygame.Vector2(caster.rect.center) + caster.direction * 100 # A 100px de distância
    
    # O "projétil" da bomba em si. Poderia ter uma classe Projectile especial.
    # Aqui, vamos simplificar e criar a explosão diretamente.
    # Para um projétil que viaja e *depois* explode, seria mais complexo.
    # Vamos fazer a bomba explodir "no local" para simplificar.
    
    # Para este exemplo, a "bomba" é um projétil que cria uma explosão ao morrer.
    # Para simplificar ainda mais, criamos a explosão diretamente.
    # Não, vamos fazer um projétil que, ao morrer, cria uma explosão.
    
    # Vamos usar a ideia original: projétil que viaja e explode.
    # O projétil da bomba terá um 'on_death' callback ou tipo especial.
    # Por ora, vamos criar um projétil simples que não faz nada visível,
    # e a *função de ativação* retorna a explosão em si (como se já tivesse explodido)
    # AVISO: Isso é uma simplificação. Idealmente, o projétil BloodBomb viajaria.
    
    # Solução mais simples para o exemplo: a bomba é instantânea
    # explosion_pos = caster.rect.center + caster.direction * 50 # Onde a bomba "explode"
    # return [BloodBombExplosion(explosion_pos)] # Retorna uma lista de sprites de efeito

    # Melhor: Lança um projétil que, ao "morrer" (atingir alcance ou tempo), causa a explosão.
    # Vamos criar um tipo especial de projétil para a bomba.
    class BloodBombProjectile(Projectile):
        def __init__(self, pos, direction):
            super().__init__(pos, direction, 'blood_bomb_projectile', speed=7, damage=0, lifetime=1000) # Não causa dano direto
            self.exploded = False

        def update(self): # Sobrescreve para checar explosão
            super().update()
            if not self.alive() and not self.exploded: # Se foi "killed" (saiu da tela ou lifetime)
                self.exploded = True
                # Cria a explosão no local onde o projétil "morreu"
                game_state.add_effect(BloodBombExplosion(self.rect.center))


    return [BloodBombProjectile(caster.rect.center, caster.direction)]


def activate_night_beam(caster):
    # Lança um feixe rápido em linha reta
    # O projétil 'night_beam_projectile' já é comprido, dando efeito de feixe
    return [Projectile(caster.rect.center, caster.direction, 'night_beam_projectile', speed=20, damage=25, lifetime=500)]

def activate_shadow_barrier(caster):
    # Implementação futura: daria um escudo temporário ao vampiro
    # caster.is_shielded = True
    # caster.shield_timer = pygame.time.get_ticks() + 5000 # 5 segundos de escudo
    print("Shadow Barrier (Not Implemented Yet)")
    return []


SPELLS_DATA = {
    'blood_bomb': {
        'name': "Blood Bomb",
        'unlock_level': 3,
        'cooldown': 8000, # 8 segundos
        'activate_func': activate_blood_bomb,
        'key_to_equip': pygame.K_1 # Tecla para equipar no castelo
    },
    'night_beam': {
        'name': "Night Beam",
        'unlock_level': 6,
        'cooldown': 5000, # 5 segundos
        'activate_func': activate_night_beam,
        'key_to_equip': pygame.K_2
    },
    # 'shadow_barrier': {
    #     'name': "Shadow Barrier",
    #     'unlock_level': 9,
    #     'cooldown': 15000, # 15 segundos
    #     'activate_func': activate_shadow_barrier,
    #     'key_to_equip': pygame.K_3
    # }
}


# === GERENCIAMENTO DE JOGO ===
class GameState:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Vampire Legacy Evolved")
        self.clock = pygame.time.Clock()
        
        self.vampire = None
        self.humans = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group() # Projéteis do Vampiro
        self.effects = pygame.sprite.Group() # Para explosões, etc.
        self.all_sprites = pygame.sprite.Group()

        self.current_map = "castle" # castle, hunt_forest, hunt_village
        self.current_stage = 0
        self.game_over_flag = False
        self.restart_timer = 0
        self.paused = False
        
        self.setup_game()

    def setup_game(self):
        self.vampire = Vampire((WIDTH // 2, HEIGHT // 2))
        
        self.all_sprites.empty()
        self.humans.empty()
        self.enemies.empty()
        self.projectiles.empty()
        self.effects.empty()

        self.all_sprites.add(self.vampire)
        
        self.current_stage = 0 # Resetar ao iniciar novo jogo
        self.game_over_flag = False
        self.change_map("castle") # Começa no castelo

    def change_map(self, map_name):
        self.current_map = map_name
        
        # Limpar entidades específicas do mapa anterior (exceto o vampiro)
        for group in [self.humans, self.enemies, self.projectiles, self.effects]:
            for entity in group: entity.kill() # kill() remove de todos os grupos

        if map_name == "castle":
            print("Entered the Castle. It's safe here.")
            # No castelo, o vampiro pode se preparar. Sem inimigos.
        elif "hunt" in map_name:
            self.current_stage = 0 # Resetar estágio ao entrar em um novo mapa de caça
            self.start_new_stage()

    def start_new_stage(self):
        self.current_stage += 1
        print(f"--- Stage {self.current_stage} ---")

        # Limpar humanos e inimigos da fase anterior
        for h in self.humans: h.kill()
        for e in self.enemies: e.kill()
        # Projéteis e efeitos podem persistir por um curto período ou serem limpos também
        # for p in self.projectiles: p.kill()
        # for ef in self.effects: ef.kill()


        num_humans = BASE_HUMANS_PER_STAGE + (self.current_stage -1) * HUMANS_INCREMENT_PER_STAGE
        num_enemies = BASE_ENEMIES_PER_STAGE + (self.current_stage-1) * ENEMIES_INCREMENT_PER_STAGE
        enemy_current_speed = ENEMY_BASE_SPEED + (self.current_stage-1) * ENEMY_SPEED_INCREMENT_PER_STAGE

        for _ in range(num_humans):
            h_pos = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
            human = Human(h_pos)
            self.humans.add(human)
            self.all_sprites.add(human)

        for _ in range(num_enemies):
            e_pos = (random.choice([random.randint(0,50), random.randint(WIDTH-50, WIDTH)]), 
                     random.choice([random.randint(0,50), random.randint(HEIGHT-50, HEIGHT)])) # Spawn nas bordas
            enemy = Enemy(e_pos, enemy_current_speed)
            # Evitar spawn em cima do vampiro
            while pygame.Rect(e_pos, (30,30)).colliderect(self.vampire.rect.inflate(100,100)) :
                 e_pos = (random.choice([random.randint(0,50), random.randint(WIDTH-50, WIDTH)]), 
                          random.choice([random.randint(0,50), random.randint(HEIGHT-50, HEIGHT)]))
            enemy.rect.topleft = e_pos
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def add_projectile(self, projectile):
        if projectile:
            if isinstance(projectile, list): # Se for uma lista de projéteis
                for p in projectile:
                    self.projectiles.add(p)
                    self.all_sprites.add(p)
            else: # Se for um único projétil
                self.projectiles.add(projectile)
                self.all_sprites.add(projectile)
    
    def add_effect(self, effect_sprite):
        if effect_sprite:
            self.effects.add(effect_sprite)
            self.all_sprites.add(effect_sprite)


    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False # Sinaliza para sair do loop principal
            
            if self.game_over_flag:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.setup_game() # Reinicia
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.paused = not self.paused
                if self.paused: continue

                # Mudança de Mapa (atalhos)
                if event.key == pygame.K_F1: self.change_map("castle")
                elif event.key == pygame.K_F2: self.change_map("hunt_forest")
                elif event.key == pygame.K_F3: self.change_map("hunt_village")
                
                # Atirar
                if event.key == pygame.K_SPACE:
                    new_projectiles = self.vampire.shoot()
                    self.add_projectile(new_projectiles)
                
                # Usar Magia Equipada
                if event.key == pygame.K_f: # 'F' para Fire spell
                    spell_effect = self.vampire.use_equipped_spell()
                    if spell_effect: # Pode retornar projéteis ou efeitos
                        if isinstance(spell_effect, list): # Lista de sprites (projéteis ou efeitos)
                            for item in spell_effect:
                                if isinstance(item, Projectile): # Se for projétil
                                    self.add_projectile(item)
                                else: # Se for um efeito visual (como explosão)
                                    self.add_effect(item)
                        # else: # Se for um único sprite (não usado nos exemplos atuais)
                        #     if isinstance(spell_effect, Projectile): self.add_projectile(spell_effect)
                        #     else: self.add_effect(spell_effect)


                # Equipar Magias (somente no castelo)
                if self.current_map == "castle":
                    for spell_id, spell_data_entry in SPELLS_DATA.items():
                        if event.key == spell_data_entry['key_to_equip']:
                            self.vampire.equip_spell(spell_id)
                            break # Para de checar outras teclas de magia
                    if event.key == pygame.K_0: # Desequipar
                        self.vampire.equip_spell(None)


        if not self.game_over_flag and not self.paused:
            self.vampire.update(keys, self) # Passa o game_state para o vampiro
        return True


    def update_game_logic(self):
        if self.game_over_flag or self.paused:
            return

        # Atualizar inimigos (apenas se não estiver no castelo)
        if self.current_map != "castle":
            for enemy in self.enemies:
                enemy.update(self.vampire.rect.center)
                # Colisão Vampiro-Inimigo
                if self.vampire.rect.colliderect(enemy.rect):
                    if self.vampire.take_damage(15): # Inimigo causa 15 de dano
                        self.game_over_flag = True
                        self.restart_timer = pygame.time.get_ticks() + 5000 # 5 seg para reiniciar
                        print("Vampire Died!")
                    else: # Empurra o inimigo um pouco para evitar dano contínuo imediato
                        enemy.rect.move_ip( (enemy.rect.centerx - self.vampire.rect.centerx) * 0.2, 
                                            (enemy.rect.centery - self.vampire.rect.centery) * 0.2)


        # Atualizar projéteis e efeitos
        self.projectiles.update()
        self.effects.update() # Atualiza e remove efeitos expirados (como explosões)

        # Colisões
        # Vampiro sugando Humanos
        if self.current_map != "castle":
            collided_humans = pygame.sprite.spritecollide(self.vampire, self.humans, False)
            for human in collided_humans:
                if not human.sucked:
                    human.get_sucked()
                    self.vampire.gain_exp(EXP_PER_HUMAN)
                    self.vampire.increase_vampiric_strength()
                    # Curar um pouco ao sugar
                    self.vampire.hp = min(self.vampire.max_hp, self.vampire.hp + 5)


        # Projéteis atingindo Inimigos
        # (projéteis normais)
        for proj in self.projectiles:
            # Checar se projétil é uma bomba, para não causar dano antes da explosão
            if isinstance(proj, Projectile) and not proj.image_key == 'blood_bomb_projectile':
                hit_enemies = pygame.sprite.spritecollide(proj, self.enemies, True) # Inimigo morre
                for _ in hit_enemies:
                    self.vampire.gain_exp(EXP_PER_ENEMY)
                    proj.kill() # Projétil desaparece ao atingir

        # Efeitos (ex: explosão da Bomba de Sangue) atingindo Inimigos
        for effect in self.effects:
            if isinstance(effect, BloodBombExplosion): # Apenas explosões causam dano
                # Usar um rect temporário para a área de dano da explosão, se necessário
                # Aqui, a própria sprite da explosão é a área de dano
                exploded_enemies = pygame.sprite.spritecollide(effect, self.enemies, True) # Inimigos morrem
                for _ in exploded_enemies:
                    self.vampire.gain_exp(EXP_PER_ENEMY * 2) # Explosão dá mais EXP
                # A explosão não desaparece ao atingir, ela tem sua própria duração


        # Verificar condição de próxima fase
        if self.current_map != "castle":
            all_sucked = True
            if not self.humans: # Se não houver humanos (ex: todos mortos em fases anteriores e nenhum novo)
                all_sucked = False # Evita loop infinito se não houver humanos para sugar
            for human in self.humans:
                if not human.sucked:
                    all_sucked = False
                    break
            if all_sucked and len(self.humans) > 0: # Precisa ter tido humanos para sugar
                self.start_new_stage()


    def draw_hud(self):
        # Informações do Vampiro
        hp_text = FONT_SMALL.render(f"HP: {int(self.vampire.hp)}/{self.vampire.max_hp}", True, WHITE)
        level_text = FONT_SMALL.render(f"Level: {self.vampire.level} ({self.vampire.exp}/{EXP_TO_LEVEL_UP_BASE * self.vampire.level})", True, WHITE)
        title_text = FONT_SMALL.render(f"Title: {self.vampire.title}", True, WHITE)
        strength_text = FONT_SMALL.render(f"Strength: {self.vampire.vampiric_strength}", True, WHITE)
        
        self.screen.blit(hp_text, (10, 10))
        self.screen.blit(level_text, (10, 30))
        self.screen.blit(title_text, (10, 50))
        self.screen.blit(strength_text, (10, 70))

        # Informações do Mapa/Fase
        map_info_text = FONT_SMALL.render(f"Map: {self.current_map.replace('_', ' ').title()}", True, WHITE)
        self.screen.blit(map_info_text, (WIDTH - map_info_text.get_width() - 10, 10))
        if "hunt" in self.current_map:
            stage_text = FONT_SMALL.render(f"Stage: {self.current_stage}", True, WHITE)
            self.screen.blit(stage_text, (WIDTH - stage_text.get_width() - 10, 30))
            
            # Contagem de humanos vivos
            alive_humans = sum(1 for h in self.humans if not h.sucked)
            humans_text = FONT_SMALL.render(f"Humans Left: {alive_humans}", True, WHITE if alive_humans > 0 else YELLOW)
            self.screen.blit(humans_text, (WIDTH - humans_text.get_width() - 10, 50))


        # Informações de Magias
        if self.vampire.equipped_spell_id:
            spell_name = self.vampire.spells[self.vampire.equipped_spell_id]['data']['name']
            spell_cooldown_total = self.vampire.spells[self.vampire.equipped_spell_id]['data']['cooldown']
            spell_last_used = self.vampire.spells[self.vampire.equipped_spell_id]['last_used']
            time_since_last_used = pygame.time.get_ticks() - spell_last_used
            cooldown_remaining = max(0, spell_cooldown_total - time_since_last_used)
            
            spell_status = f"Equipped: {spell_name}"
            if cooldown_remaining > 0:
                spell_status += f" (CD: {cooldown_remaining/1000:.1f}s)"
            else:
                spell_status += " (Ready!)"
            
            equipped_spell_text = FONT_SMALL.render(spell_status, True, WHITE)
            self.screen.blit(equipped_spell_text, (10, HEIGHT - 30))

        if self.current_map == "castle":
            cast_info_y = HEIGHT - 100
            help_text = FONT_SMALL.render("In Castle: Press number keys to equip spells (0 to unequip).", True, YELLOW)
            self.screen.blit(help_text, (10, cast_info_y))
            cast_info_y += 20
            for spell_id, spell_info in self.vampire.spells.items():
                if spell_info['unlocked']:
                    s_text = f"[{SPELLS_DATA[spell_id]['key_to_equip'].__repr__()[-2]}] {spell_info['data']['name']}"
                    if self.vampire.equipped_spell_id == spell_id:
                         s_text += " (EQUIPPED)"
                    spell_list_text = FONT_SMALL.render(s_text, True, GREEN if self.vampire.equipped_spell_id == spell_id else WHITE)
                    self.screen.blit(spell_list_text, (10, cast_info_y))
                    cast_info_y += 20


    def draw_elements(self):
        # Fundo
        if "hunt" in self.current_map:
            self.screen.fill(GREEN)
        elif self.current_map == "castle":
            self.screen.fill(BLACK) # Castelo é escuro
        else:
            self.screen.fill(GRAY) # Default

        self.all_sprites.draw(self.screen)
        self.draw_hud()

        if self.game_over_flag:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0, 180)) # Semi-transparente escuro
            self.screen.blit(overlay, (0,0))

            text = FONT_LARGE.render("VOCÊ MORREU!", True, RED)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            self.screen.blit(text, text_rect)
            
            restart_msg = "Pressione 'R' para reiniciar"
            if pygame.time.get_ticks() < self.restart_timer:
                 time_left = (self.restart_timer - pygame.time.get_ticks()) // 1000
                 restart_msg = f"Reiniciando em {time_left}s... ou pressione 'R'"

            restart_text = FONT_MEDIUM.render(restart_msg, True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            self.screen.blit(restart_text, restart_rect)
            
            if pygame.time.get_ticks() > self.restart_timer: # Auto-restart se 'R' não for pressionado
                self.setup_game()
        
        if self.paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0, 150))
            self.screen.blit(overlay, (0,0))
            pause_text = FONT_LARGE.render("PAUSADO", True, YELLOW)
            self.screen.blit(pause_text, pause_text.get_rect(center=(WIDTH//2, HEIGHT//2)))


        pygame.display.flip()


    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            if not self.handle_input(): # handle_input retorna False se QUIT
                running = False
                continue

            self.update_game_logic()
            self.draw_elements()
            
        pygame.quit()

# === PONTO DE ENTRADA ===
if __name__ == '__main__':
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) # Necessário para SPRITES['night_beam_projectile'] se usar convert_alpha()
    create_sprites() # Criar sprites depois de set_mode se usar convert_alpha
    
    game_state = GameState() # Instancia o gerenciador
    game_state.run()