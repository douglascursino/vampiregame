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
VAMPIRE_START_HP = 100
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
        self.last_moved_direction = pygame.Vector2(1, 0) 
        self.vampiric_strength = 0
        self.shoot_cooldown = BASE_SHOOT_COOLDOWN
        self.last_shot_time = 0
        
        self.spells = {}
        self.equipped_spell_id = None
        self.check_spell_unlocks()

    def update(self, keys, game_state_ref): # Renomeado para clareza, ainda se refere à instância game_state
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        if dx != 0 or dy != 0:
            self.direction = pygame.Vector2(dx, dy).normalize()
            self.last_moved_direction = self.direction 
            self.rect.x += self.speed * self.direction.x
            self.rect.y += self.speed * self.direction.y
        
        self.rect.clamp_ip(screen.get_rect()) 
        self.update_title()
        
        if game_state_ref.current_map == "castle" and self.hp < self.max_hp:
            self.hp += 0.05 
            if self.hp > self.max_hp: self.hp = self.max_hp

    def gain_exp(self, amount):
        self.exp += amount
        exp_to_next_level = EXP_TO_LEVEL_UP_BASE * self.level
        if self.exp >= exp_to_next_level:
            self.exp -= exp_to_next_level
            self.level += 1
            self.max_hp += 10 
            self.hp = self.max_hp 
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

            if self.last_moved_direction.length_squared() > 0:
                 shoot_direction = -self.last_moved_direction.normalize()
            else:
                 shoot_direction = pygame.Vector2(-1, 0) 

            if self.level >= BURST_SHOT_LEVEL:
                for i in range(12):
                    angle = i * 30
                    dir_vec = shoot_direction.rotate(angle) 
                    projectiles_to_add.append(Projectile(self.rect.center, dir_vec, 'projectile', PROJECTILE_SPEED))
            elif self.level >= SPREAD_SHOT_LEVEL: 
                projectiles_to_add.append(Projectile(self.rect.center, shoot_direction, 'projectile', PROJECTILE_SPEED))
                projectiles_to_add.append(Projectile(self.rect.center, shoot_direction.rotate(25), 'projectile', PROJECTILE_SPEED))
                projectiles_to_add.append(Projectile(self.rect.center, shoot_direction.rotate(-25), 'projectile', PROJECTILE_SPEED))
            else: 
                projectiles_to_add.append(Projectile(self.rect.center, shoot_direction, 'projectile', PROJECTILE_SPEED))
            
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
            
            cast_direction = self.last_moved_direction
            if cast_direction.length_squared() == 0: 
                cast_direction = pygame.Vector2(1,0) 

            return spell['data']['activate_func'](self, cast_direction)
        else:
            pass
        return None
        
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            return True 
        return False 

class Human(GameObject):
    def __init__(self, pos):
        super().__init__('human_alive', pos)
        self.sucked = False

    def get_sucked(self):
        if not self.sucked:
            self.sucked = True
            self.image = SPRITES['human_dead']

class Enemy(GameObject):
    def __init__(self, pos, speed):
        super().__init__('enemy', pos)
        self.speed = speed

    def update(self, target_pos):
        direction_to_target = pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)
        if direction_to_target.length() > 0:
            direction_to_target = direction_to_target.normalize()
            self.rect.move_ip(direction_to_target * self.speed)

class Projectile(GameObject):
    def __init__(self, pos, direction, image_key='projectile', speed=PROJECTILE_SPEED, damage=10, lifetime=2000):
        super().__init__(image_key, pos)
        if direction.length_squared() > 0:
            self.velocity = direction.normalize() * speed
        else: 
            self.velocity = pygame.Vector2(0, -1) * speed 
            print("Warning: Projectile created with zero direction vector.")

        self.damage = damage
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime 

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        if not screen.get_rect().contains(self.rect) or \
           pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

class BloodBombExplosion(GameObject):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ORANGE, (40, 40), 40)
        pygame.draw.circle(self.image, RED, (40, 40), 30)
        self.rect = self.image.get_rect(center=pos)
        self.damage = 30 
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 300 

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill() 

# *** CLASSE MOVIDA PARA O ESCOPO GLOBAL ***
class BloodBombProjectile(Projectile):
    def __init__(self, pos, direction_vector):
        # image_key é 'blood_bomb_projectile', damage é 0 (não causa dano direto)
        super().__init__(pos, direction_vector, 'blood_bomb_projectile', speed=7, damage=0, lifetime=1000) 
        self.exploded = False

    def update(self): 
        super().update()
        # Acessa a instância global 'game_state' para adicionar o efeito
        # Para um design mais robusto, game_state.add_effect poderia ser passado como callback
        if not self.alive() and not self.exploded: 
            self.exploded = True
            if 'game_state' in globals(): # Checa se game_state é acessível globalmente
                game_state.add_effect(BloodBombExplosion(self.rect.center))
            else:
                print("Error: game_state not accessible in BloodBombProjectile.update()")


# === FUNÇÕES DE MAGIA ===
def activate_blood_bomb(caster, caster_direction):
    # Agora instancia a classe BloodBombProjectile que está no escopo global
    return [BloodBombProjectile(caster.rect.center, caster_direction)]

def activate_night_beam(caster, caster_direction):
    return [Projectile(caster.rect.center, caster_direction, 'night_beam_projectile', speed=20, damage=25, lifetime=500)]

def activate_shadow_barrier(caster, caster_direction):
    print("Shadow Barrier (Not Implemented Yet)")
    return []

SPELLS_DATA = {
    'blood_bomb': {
        'name': "Blood Bomb",
        'unlock_level': 3,
        'cooldown': 8000, 
        'activate_func': activate_blood_bomb,
        'key_to_equip': pygame.K_1 
    },
    'night_beam': {
        'name': "Night Beam",
        'unlock_level': 6,
        'cooldown': 5000, 
        'activate_func': activate_night_beam,
        'key_to_equip': pygame.K_2
    },
}

# === GERENCIAMENTO DE JOGO ===
class GameState:
    def __init__(self):
        pygame.display.set_caption("Vampire Legacy Evolved")
        self.clock = pygame.time.Clock()
        
        self.vampire = None
        self.humans = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group() 
        self.effects = pygame.sprite.Group() 
        self.all_sprites = pygame.sprite.Group()

        self.current_map = "castle" 
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
        
        self.current_stage = 0 
        self.game_over_flag = False
        self.paused = False # Garantir que não comece pausado
        self.restart_timer = 0 # Resetar timer

        # Resetar estado do vampiro
        self.vampire.hp = self.vampire.max_hp 
        if not hasattr(self, 'initial_vampire_state_saved'): # Salvar estado inicial apenas uma vez
            self.initial_vampire_exp = self.vampire.exp
            self.initial_vampire_level = self.vampire.level
            self.initial_vampire_strength = self.vampire.vampiric_strength
            self.initial_vampire_spells = self.vampire.spells.copy() # Cópia rasa, ok para esta estrutura
            self.initial_vampire_state_saved = True

        self.vampire.exp = 0 # Ou self.initial_vampire_exp se quiser persistir entre mortes (não é o caso aqui)
        self.vampire.level = 1 # Ou self.initial_vampire_level
        self.vampire.vampiric_strength = 0 # Ou self.initial_vampire_strength
        self.vampire.shoot_cooldown = BASE_SHOOT_COOLDOWN
        self.vampire.equipped_spell_id = None
        self.vampire.spells = {} # Resetar magias aprendidas, elas serão re-desbloqueadas pelo nível
        self.vampire.check_spell_unlocks() 
        self.vampire.update_title()

        self.change_map("castle") 

    def change_map(self, map_name):
        self.current_map = map_name
        
        for group in [self.humans, self.enemies, self.projectiles, self.effects]:
            for entity in group: entity.kill() 

        if map_name == "castle":
            print("Entered the Castle. It's safe here.")
        elif "hunt" in map_name:
            self.current_stage = 0 
            self.start_new_stage()

    def start_new_stage(self):
        self.current_stage += 1
        print(f"--- Stage {self.current_stage} ---")

        for h in self.humans: h.kill()
        for e in self.enemies: e.kill()

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
                     random.choice([random.randint(0,50), random.randint(HEIGHT-50, HEIGHT)])) 
            enemy = Enemy(e_pos, enemy_current_speed)
            while self.vampire and pygame.Rect(e_pos, (30,30)).colliderect(self.vampire.rect.inflate(100,100)) :
                 e_pos = (random.choice([random.randint(0,50), random.randint(WIDTH-50, WIDTH)]), 
                          random.choice([random.randint(0,50), random.randint(HEIGHT-50, HEIGHT)]))
            enemy.rect.topleft = e_pos
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def add_projectile(self, projectile_or_list):
        if projectile_or_list:
            if isinstance(projectile_or_list, list): 
                for p_item in projectile_or_list:
                    if p_item: 
                        self.projectiles.add(p_item)
                        self.all_sprites.add(p_item)
            else: 
                self.projectiles.add(projectile_or_list)
                self.all_sprites.add(projectile_or_list)
    
    def add_effect(self, effect_sprite):
        if effect_sprite:
            self.effects.add(effect_sprite)
            self.all_sprites.add(effect_sprite)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False 
            
            if self.game_over_flag:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.setup_game() 
                continue # Não processar mais inputs se game over e não for 'R'

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    self.paused = not self.paused
                    print(f"Game Paused: {self.paused}")
                
                if self.paused and event.key != pygame.K_ESCAPE: # Se pausado, só ESC despausa
                    continue


                if event.key == pygame.K_F1: self.change_map("castle")
                elif event.key == pygame.K_F2: self.change_map("hunt_forest")
                elif event.key == pygame.K_F3: self.change_map("hunt_village")
                
                if event.key == pygame.K_SPACE:
                    new_projectiles = self.vampire.shoot()
                    self.add_projectile(new_projectiles)
                
                if event.key == pygame.K_f: 
                    spell_effect_sprites = self.vampire.use_equipped_spell()
                    if spell_effect_sprites: 
                        for item in spell_effect_sprites: 
                            if isinstance(item, Projectile): 
                                self.add_projectile(item) 
                            else: # Qualquer outra coisa é um efeito
                                self.add_effect(item) 

                if self.current_map == "castle":
                    for spell_id, spell_data_entry in SPELLS_DATA.items():
                        if event.key == spell_data_entry['key_to_equip']:
                            self.vampire.equip_spell(spell_id)
                            break 
                    if event.key == pygame.K_0: 
                        self.vampire.equip_spell(None)

        if not self.game_over_flag and not self.paused:
            self.vampire.update(keys, self) 
        return True

    def update_game_logic(self):
        if self.game_over_flag or self.paused:
            return

        if self.current_map != "castle":
            for enemy in self.enemies:
                enemy.update(self.vampire.rect.center)
                if self.vampire.rect.colliderect(enemy.rect):
                    if self.vampire.take_damage(15): 
                        self.game_over_flag = True
                        self.restart_timer = pygame.time.get_ticks() + 5000 
                        print("Vampire Died!")
                        # Não precisa de break aqui, pois o game_over_flag já para a lógica no início da função
                    else: 
                        push_vector = (pygame.Vector2(enemy.rect.center) - pygame.Vector2(self.vampire.rect.center))
                        if push_vector.length_squared() > 0:
                            push_vector = push_vector.normalize() * 5 
                            enemy.rect.move_ip(push_vector.x, push_vector.y)
                        else: 
                            enemy.rect.x += 10 # Evita ficar preso se exatamente sobreposto

        self.projectiles.update()
        self.effects.update() 

        if self.current_map != "castle":
            collided_humans = pygame.sprite.spritecollide(self.vampire, self.humans, False)
            for human in collided_humans:
                if not human.sucked:
                    human.get_sucked()
                    self.vampire.gain_exp(EXP_PER_HUMAN)
                    self.vampire.increase_vampiric_strength()
                    self.vampire.hp = min(self.vampire.max_hp, self.vampire.hp + 5)

        # Agora BloodBombProjectile está definido globalmente
        for proj in self.projectiles:
            if not isinstance(proj, BloodBombProjectile): 
                if hasattr(proj, 'damage') and proj.damage > 0:
                    hit_enemies = pygame.sprite.spritecollide(proj, self.enemies, True) 
                    for _ in hit_enemies:
                        self.vampire.gain_exp(EXP_PER_ENEMY)
                        proj.kill() 

        for effect in self.effects:
            if isinstance(effect, BloodBombExplosion): 
                exploded_enemies = pygame.sprite.spritecollide(effect, self.enemies, True) 
                for _ in exploded_enemies:
                    self.vampire.gain_exp(EXP_PER_ENEMY * 2) 

        if self.current_map != "castle" and self.current_stage > 0: # Só checa avanço se em mapa de caça e estágio iniciado
            all_sucked = True
            if not self.humans: 
                pass # Se não há humanos, a condição de "all_sucked" é trivialmente verdadeira para humanos
            else: 
                for human in self.humans:
                    if not human.sucked:
                        all_sucked = False
                        break
            
            if all_sucked and not self.enemies:
                 if self.humans: 
                    print("All humans sucked and enemies defeated! Advancing stage.")
                    self.start_new_stage()
                 elif not self.humans: 
                    print("All enemies defeated (no humans this stage)! Advancing stage.")
                    self.start_new_stage()

    def draw_hud(self):
        hp_text = FONT_SMALL.render(f"HP: {int(self.vampire.hp)}/{self.vampire.max_hp}", True, WHITE)
        level_text = FONT_SMALL.render(f"Level: {self.vampire.level} ({self.vampire.exp}/{EXP_TO_LEVEL_UP_BASE * self.vampire.level})", True, WHITE)
        title_text = FONT_SMALL.render(f"Title: {self.vampire.title}", True, WHITE)
        strength_text = FONT_SMALL.render(f"Strength: {self.vampire.vampiric_strength}", True, WHITE)
        
        screen.blit(hp_text, (10, 10))
        screen.blit(level_text, (10, 30))
        screen.blit(title_text, (10, 50))
        screen.blit(strength_text, (10, 70))

        map_info_text = FONT_SMALL.render(f"Map: {self.current_map.replace('_', ' ').title()}", True, WHITE)
        screen.blit(map_info_text, (WIDTH - map_info_text.get_width() - 10, 10))
        if "hunt" in self.current_map:
            stage_text = FONT_SMALL.render(f"Stage: {self.current_stage}", True, WHITE)
            screen.blit(stage_text, (WIDTH - stage_text.get_width() - 10, 30))
            
            alive_humans = sum(1 for h in self.humans if not h.sucked)
            humans_text = FONT_SMALL.render(f"Humans Left: {alive_humans}", True, WHITE if alive_humans > 0 else YELLOW)
            screen.blit(humans_text, (WIDTH - humans_text.get_width() - 10, 50))
            
            enemies_left = len(self.enemies)
            enemies_text = FONT_SMALL.render(f"Enemies Left: {enemies_left}", True, WHITE if enemies_left > 0 else YELLOW)
            screen.blit(enemies_text, (WIDTH - enemies_text.get_width() - 10, 70))

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
            screen.blit(equipped_spell_text, (10, HEIGHT - 30))

        if self.current_map == "castle":
            cast_info_y = HEIGHT - 100
            help_text = FONT_SMALL.render("In Castle: Press number keys to equip spells (0 to unequip).", True, YELLOW)
            screen.blit(help_text, (10, cast_info_y))
            cast_info_y += 20
            for spell_id, spell_info_dict in self.vampire.spells.items():
                if spell_info_dict['unlocked']:
                    key_num = SPELLS_DATA[spell_id]['key_to_equip']
                    key_name = pygame.key.name(key_num) 
                    s_text = f"[{key_name.upper()}] {spell_info_dict['data']['name']}"
                    if self.vampire.equipped_spell_id == spell_id:
                         s_text += " (EQUIPPED)"
                    spell_list_text = FONT_SMALL.render(s_text, True, GREEN if self.vampire.equipped_spell_id == spell_id else WHITE)
                    screen.blit(spell_list_text, (10, cast_info_y))
                    cast_info_y += 20

    def draw_elements(self):
        if "hunt" in self.current_map:
            screen.fill(GREEN)
        elif self.current_map == "castle":
            screen.fill(BLACK) 
        else:
            screen.fill(GRAY) 

        self.all_sprites.draw(screen)
        self.draw_hud()

        if self.game_over_flag:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0, 180)) 
            screen.blit(overlay, (0,0))

            text = FONT_LARGE.render("VOCÊ MORREU!", True, RED)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            screen.blit(text, text_rect)
            
            restart_msg = "Pressione 'R' para reiniciar"
            current_time = pygame.time.get_ticks()
            if self.restart_timer > 0 and current_time < self.restart_timer : 
                 time_left = (self.restart_timer - current_time) // 1000
                 restart_msg = f"Reiniciando em {time_left}s... ou pressione 'R'"
            elif self.restart_timer > 0 and current_time >= self.restart_timer: 
                self.setup_game() # Auto-restart
                return # Evita desenhar o resto desta frame

            restart_text = FONT_MEDIUM.render(restart_msg, True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            screen.blit(restart_text, restart_rect)
        
        if self.paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0, 150))
            screen.blit(overlay, (0,0))
            pause_text = FONT_LARGE.render("PAUSADO", True, YELLOW)
            screen.blit(pause_text, pause_text.get_rect(center=(WIDTH//2, HEIGHT//2)))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            if not self.handle_input(): 
                running = False
                continue

            self.update_game_logic()
            self.draw_elements()
            
        pygame.quit()

# === PONTO DE ENTRADA ===
if __name__ == '__main__':
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
    create_sprites() 
    
    game_state = GameState() # Cria a instância global de GameState
    game_state.run()