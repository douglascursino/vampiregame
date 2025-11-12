--- START OF FILE main v12.py ---

import pygame
import random
import math
import os
import json

pygame.init()
pygame.font.init()

# === CONSTANTES ===
WIDTH, HEIGHT = 800, 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
DARK_RED = (100, 0, 0)
SKIN = (255, 220, 200)
PURPLE = (138, 43, 226)
BLUE = (0, 100, 255)
GRAY = (180, 180, 180)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GREEN_DARK = (0, 100, 0)
BROWN = (139, 69, 19)
BONE_WHITE = (245, 245, 220)
GREEN = (50, 168, 82)

VAMPIRE_START_HP = 100
VAMPIRE_HP_PER_LEVEL = 10
VAMPIRE_SPEED = 5
PROJECTILE_SPEED = 10
BASE_PROJECTILE_DAMAGE = 10
BASE_SHOOT_COOLDOWN = 1000
MIN_SHOOT_COOLDOWN = 150
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
SPREAD_SHOT_LEVEL = 5
BURST_SHOT_LEVEL = 10

FONT_SMALL = pygame.font.SysFont("arial", 20)
FONT_MEDIUM = pygame.font.SysFont("arial", 30)
FONT_LARGE = pygame.font.SysFont("arial", 40)

ASSET_PATH = "assets"
SPRITE_PATH = os.path.join(ASSET_PATH, "sprites")
SAVE_FILENAME = "savegame.json"

VAMPIRE_SIZE = (60, 60)
HUMAN_SIZE = (40, 40)
ENEMY_DEFAULT_SIZE = (100, 100)
ENEMY_SLIME_SIZE = (100, 100)
ENEMY_GHOUL_SIZE = (100, 100)
ENEMY_BAT_SIZE = (100, 100)
ENEMY_SKELETON_SIZE = (100, 100)
ENEMY_FF_SIZE = (130, 130)
ENEMY_FIREELEMENTAL_SIZE = (130, 130)
ENEMY_DARKANGEL_SIZE = (100, 100)
ENEMY_MONSTER_SIZE = (100, 100)
PROJECTILE_SIZE_NORMAL = (15, 15)
PROJECTILE_SIZE_BLOODBOMB = (25, 25)
PROJECTILE_SIZE_NIGHTBEAM = (80, 15)

SPRITES = {}
GRASS_TILE_IMG = None
VAMPIRE_BASE_SPRITE_KEY = 'vampire_base' # Corresponde a assets/sprites/vampire_base.png

# Definição das Armaduras
# As chaves aqui ('plate_armor', 'golden_armor', etc.) serão usadas para
# construir os nomes dos arquivos de sprite (ex: 'vampire_plate_armor.png')
ARMORS_DATA = {
    'plate_armor': {
        'name': "Plate Armor",      # Nome exibido no HUD
        'unlock_level': 3,          # Nível para desbloquear
        'hp_bonus': 15,             # Bônus de HP
        'damage_bonus': 2,          # Bônus de dano de ataque
        'key_to_equip': pygame.K_7  # Tecla para equipar
    },
    'golden_armor': {
        'name': "Golden Armor",
        'unlock_level': 7,
        'hp_bonus': 30,
        'damage_bonus': 4,
        'key_to_equip': pygame.K_8
    },
    'black_armor': {
        'name': "Black Armor",
        'unlock_level': 11,
        'hp_bonus': 50,
        'damage_bonus': 6,
        'key_to_equip': pygame.K_9
    },
    'dark_angel_armor': {
        'name': "Dark Angel Armor",
        'unlock_level': 15,
        'hp_bonus': 75,
        'damage_bonus': 8,
        'key_to_equip': pygame.K_6
    },
    'elf_vampire_armor': {
        'name': "Elf Vampire Armor",
        'unlock_level': 20,
        'hp_bonus': 100,
        'damage_bonus': 10,
        'key_to_equip': pygame.K_5
    }
}
ARMOR_UNEQUIP_KEY = pygame.K_MINUS # Tecla para desequipar (volta para vampire_base)


def load_image(filepath, size=None, use_alpha=True):
    try:
        image = pygame.image.load(filepath)
        if use_alpha: image = image.convert_alpha()
        else: image = image.convert()
        if size: image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Erro ao carregar imagem '{filepath}': {e}.")
        if size:
            fallback_surface = pygame.Surface(size, pygame.SRCALPHA)
            fallback_surface.fill((255, 0, 255, 100)) 
            pygame.draw.rect(fallback_surface, WHITE, fallback_surface.get_rect(), 1)
            return fallback_surface
        return None

def create_sprites_and_tiles():
    global GRASS_TILE_IMG, SPRITES

    # Carregar sprite base do vampiro (vampire_base.png)
    SPRITES[VAMPIRE_BASE_SPRITE_KEY] = load_image(os.path.join(SPRITE_PATH, f"{VAMPIRE_BASE_SPRITE_KEY}.png"), VAMPIRE_SIZE)
    if not SPRITES[VAMPIRE_BASE_SPRITE_KEY] or (SPRITES[VAMPIRE_BASE_SPRITE_KEY].get_at((0,0))[:3] == (255,0,255)):
        print(f"AVISO: Sprite base do vampiro '{VAMPIRE_BASE_SPRITE_KEY}.png' não encontrado ou é fallback. Criando fallback visual.")
        fallback_vamp_surf = pygame.Surface(VAMPIRE_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(fallback_vamp_surf, DARK_RED, (VAMPIRE_SIZE[0]*0.2, 0, VAMPIRE_SIZE[0]*0.6, VAMPIRE_SIZE[1]*0.8)) 
        pygame.draw.circle(fallback_vamp_surf, SKIN, (VAMPIRE_SIZE[0]//2, VAMPIRE_SIZE[1]*0.15), VAMPIRE_SIZE[0]*0.13) 
        SPRITES[VAMPIRE_BASE_SPRITE_KEY] = fallback_vamp_surf

    # Carregar sprites de armadura do vampiro (ex: vampire_plate_armor.png)
    for armor_id in ARMORS_DATA.keys():
        sprite_key_armor = f"vampire_{armor_id}" # Constrói "vampire_plate_armor", etc.
        filepath_armor = os.path.join(SPRITE_PATH, f"{sprite_key_armor}.png")
        SPRITES[sprite_key_armor] = load_image(filepath_armor, VAMPIRE_SIZE)
        # load_image já lida com fallbacks se o sprite da armadura não existir (retorna superfície magenta).

    SPRITES['human_alive'] = load_image(os.path.join(SPRITE_PATH, "human_alive.png"), HUMAN_SIZE)
    SPRITES['human_dead'] = load_image(os.path.join(SPRITE_PATH, "human_dead.png"), HUMAN_SIZE)
    SPRITES['enemy_slime'] = load_image(os.path.join(SPRITE_PATH, "enemy_slime.png"), ENEMY_SLIME_SIZE)
    SPRITES['enemy_ghoul'] = load_image(os.path.join(SPRITE_PATH, "enemy_ghoul.png"), ENEMY_GHOUL_SIZE)
    SPRITES['enemy_bat'] = load_image(os.path.join(SPRITE_PATH, "enemy_bat.png"), ENEMY_BAT_SIZE)
    SPRITES['enemy_skeleton'] = load_image(os.path.join(SPRITE_PATH, "enemy_skeleton.png"), ENEMY_SKELETON_SIZE)
    SPRITES['enemy_ff'] = load_image(os.path.join(SPRITE_PATH, "enemy_ff.png"), ENEMY_FF_SIZE)
    SPRITES['enemy_fireelemental'] = load_image(os.path.join(SPRITE_PATH, "enemy_fireelemental.png"), ENEMY_FF_SIZE)
    SPRITES['enemy_darkangel'] = load_image(os.path.join(SPRITE_PATH, "enemy_darkangel.png"), ENEMY_FF_SIZE)
    SPRITES['enemy_monster'] = load_image(os.path.join(SPRITE_PATH, "enemy_monster.png"), ENEMY_FF_SIZE)
    SPRITES['projectile'] = load_image(os.path.join(SPRITE_PATH, "projectile.png"), PROJECTILE_SIZE_NORMAL)
    SPRITES['blood_bomb_projectile'] = load_image(os.path.join(SPRITE_PATH, "blood_bomb_projectile.png"), PROJECTILE_SIZE_BLOODBOMB)
    SPRITES['night_beam_projectile'] = load_image(os.path.join(SPRITE_PATH, "night_beam_projectile.png"), PROJECTILE_SIZE_NIGHTBEAM)

    # Fallbacks para sprites de inimigos se não carregarem
    if not SPRITES.get('enemy_slime') or (SPRITES['enemy_slime'] and SPRITES['enemy_slime'].get_at((0,0))[:3] == (255,0,255)):
        e_surface = pygame.Surface(ENEMY_SLIME_SIZE, pygame.SRCALPHA); pygame.draw.ellipse(e_surface, PURPLE, e_surface.get_rect()); pygame.draw.circle(e_surface, RED, (10, 10), 4); pygame.draw.circle(e_surface, RED, (20, 10), 4); SPRITES['enemy_slime'] = e_surface
    if not SPRITES.get('enemy_ghoul') or (SPRITES['enemy_ghoul'] and SPRITES['enemy_ghoul'].get_at((0,0))[:3] == (255,0,255)):
        g_surface = pygame.Surface(ENEMY_GHOUL_SIZE, pygame.SRCALPHA); pygame.draw.rect(g_surface, GREEN_DARK, (5, 10, 25, 25)); pygame.draw.circle(g_surface, SKIN, (17, 10), 7); SPRITES['enemy_ghoul'] = g_surface
    if not SPRITES.get('enemy_bat') or (SPRITES['enemy_bat'] and SPRITES['enemy_bat'].get_at((0,0))[:3] == (255,0,255)):
        b_surface = pygame.Surface(ENEMY_BAT_SIZE, pygame.SRCALPHA); pygame.draw.ellipse(b_surface, BROWN, (2, 5, 26, 20)); pygame.draw.polygon(b_surface, BLACK, [(0,0), (5,10), (0,20)]); pygame.draw.polygon(b_surface, BLACK, [(30,0), (25,10), (30,20)]); SPRITES['enemy_bat'] = b_surface
    if not SPRITES.get('enemy_skeleton') or (SPRITES['enemy_skeleton'] and SPRITES['enemy_skeleton'].get_at((0,0))[:3] == (255,0,255)):
        s_surface = pygame.Surface(ENEMY_SKELETON_SIZE, pygame.SRCALPHA); pygame.draw.rect(s_surface, BONE_WHITE, (10, 5, 10, 25)); pygame.draw.circle(s_surface, BONE_WHITE, (15, 5), 5); SPRITES['enemy_skeleton'] = s_surface
    if not SPRITES.get('enemy_ff') or (SPRITES['enemy_ff'] and SPRITES['enemy_ff'].get_at((0,0))[:3] == (255,0,255)): # FF é usado como fallback para outros
        s_surface = pygame.Surface(ENEMY_FF_SIZE, pygame.SRCALPHA); pygame.draw.rect(s_surface, ORANGE, (10, 5, 10, 25)); pygame.draw.circle(s_surface, RED, (15, 5), 5); SPRITES['enemy_ff'] = s_surface
    if not SPRITES.get('enemy_fireelemental') or (SPRITES['enemy_fireelemental'] and SPRITES['enemy_fireelemental'].get_at((0,0))[:3] == (255,0,255)):
        SPRITES['enemy_fireelemental'] = SPRITES['enemy_ff'] # Reusa FF se não encontrar
    if not SPRITES.get('enemy_darkangel') or (SPRITES['enemy_darkangel'] and SPRITES['enemy_darkangel'].get_at((0,0))[:3] == (255,0,255)):
        SPRITES['enemy_darkangel'] = SPRITES['enemy_ff'] 
    if not SPRITES.get('enemy_monster') or (SPRITES['enemy_monster'] and SPRITES['enemy_monster'].get_at((0,0))[:3] == (255,0,255)):
        SPRITES['enemy_monster'] = SPRITES['enemy_ff']
    
    GRASS_TILE_IMG = load_image(os.path.join(SPRITE_PATH, "grass_tile.png"), use_alpha=False)
    if GRASS_TILE_IMG is None: print("Falha ao carregar grass_tile.png.")

class GameObject(pygame.sprite.Sprite):
    def __init__(self, image_key, pos):
        super().__init__()
        self.image_key = image_key 
        if image_key in SPRITES and SPRITES[image_key] is not None: 
            self.image = SPRITES[image_key]
        else: 
            print(f"AVISO GameObject: Chave de imagem '{image_key}' não encontrada em SPRITES. Usando fallback roxo.")
            self.image = pygame.Surface(ENEMY_DEFAULT_SIZE, pygame.SRCALPHA)
            self.image.fill(PURPLE)
        self.rect = self.image.get_rect(center=pos)

class Enemy(GameObject):
    def __init__(self, image_key, pos, speed, hp=30, exp_value=10, damage_to_vampire=15):
        super().__init__(image_key, pos)
        self.speed = speed; self.hp = hp; self.max_hp = hp
        self.exp_value = exp_value; self.damage_to_vampire = damage_to_vampire
    def update(self, target_pos):
        direction = pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)
        if direction.length() > 0: self.rect.move_ip(direction.normalize() * self.speed)
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0: self.kill(); return True
        return False

class EnemySlime(Enemy):
    def __init__(self, pos, speed_multiplier=1.0): super().__init__('enemy_slime', pos, ENEMY_BASE_SPEED * speed_multiplier, 30, 10)
class EnemyGhoul(Enemy):
    def __init__(self, pos, speed_multiplier=0.8): super().__init__('enemy_ghoul', pos, ENEMY_BASE_SPEED * speed_multiplier, 50, 15, 20)
class EnemyBat(Enemy):
    def __init__(self, pos, speed_multiplier=1.5):
        super().__init__('enemy_bat', pos, ENEMY_BASE_SPEED * speed_multiplier, 20, 8, 10)
        self.move_timer = 0; self.move_interval = 30
        self.flutter_direction = pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()
    def update(self, target_pos):
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            random_flutter = pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1))
            direction_to_target = pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)
            if direction_to_target.length_squared() > 0: self.flutter_direction = (direction_to_target.normalize()*0.7 + random_flutter.normalize()*0.3).normalize()
        self.rect.move_ip(self.flutter_direction * self.speed)
        self.rect.clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))
class EnemySkeleton(Enemy):
    def __init__(self, pos, speed_multiplier=0.6): super().__init__('enemy_skeleton', pos, ENEMY_BASE_SPEED * speed_multiplier, 70, 20, 25)
class Enemyff(Enemy): # Renomear para algo mais descritivo se for um inimigo específico
    def __init__(self, pos, speed_multiplier=0.6): super().__init__('enemy_ff', pos, ENEMY_BASE_SPEED * speed_multiplier, 70, 20, 25)
class EnemyFireelemental(Enemy):
    def __init__(self, pos, speed_multiplier=0.7): super().__init__('enemy_fireelemental', pos, ENEMY_BASE_SPEED * speed_multiplier, 72, 22, 26)    
class EnemyDarkangel(Enemy):
    def __init__(self, pos, speed_multiplier=0.7): super().__init__('enemy_darkangel', pos, ENEMY_BASE_SPEED * speed_multiplier, 72, 22, 26)    
class EnemyMonster(Enemy):
    def __init__(self, pos, speed_multiplier=0.7): super().__init__('enemy_monster', pos, ENEMY_BASE_SPEED * speed_multiplier, 72, 22, 26)    

ENEMY_TYPES = [EnemySlime, EnemyGhoul, EnemyBat, EnemySkeleton, Enemyff, EnemyFireelemental, EnemyDarkangel, EnemyMonster]

class Vampire(GameObject):
    def __init__(self, pos):
        super().__init__(VAMPIRE_BASE_SPRITE_KEY, pos) 

        self.speed = VAMPIRE_SPEED; self.exp = 0; self.level = 1; self.title = "New Vampire"
        self.max_hp_base = VAMPIRE_START_HP 
        self.hp = VAMPIRE_START_HP; self.max_hp = VAMPIRE_START_HP 
        self.direction = pygame.Vector2(1, 0); self.last_moved_direction = pygame.Vector2(1, 0)
        self.vampiric_strength = 0; self.shoot_cooldown = BASE_SHOOT_COOLDOWN; self.last_shot_time = 0
        self.base_projectile_damage = BASE_PROJECTILE_DAMAGE
        self.current_projectile_damage = BASE_PROJECTILE_DAMAGE
        self.spells = {}; self.equipped_spell_id = None
        self.unlocked_armors = set(); self.equipped_armor_id = None

        self._update_stats_from_level_and_armor() 
        self._set_image_based_on_armor()          
        self.check_spell_unlocks()
        self.check_armor_unlocks()

    def _set_image_based_on_armor(self):
        target_sprite_key = VAMPIRE_BASE_SPRITE_KEY 
        if self.equipped_armor_id: # Ex: self.equipped_armor_id é 'plate_armor'
            potential_armor_key = f"vampire_{self.equipped_armor_id}" # Constrói 'vampire_plate_armor'
            # Verifica se o sprite da armadura existe E não é o fallback magenta de load_image
            if SPRITES.get(potential_armor_key) and SPRITES[potential_armor_key].get_at((0,0))[:3] != (255,0,255):
                target_sprite_key = potential_armor_key
            else: # Se o sprite específico da armadura não foi carregado ou é fallback
                if SPRITES.get(potential_armor_key): # Se existe mas é fallback magenta
                     print(f"AVISO: Sprite para armadura '{self.equipped_armor_id}' ({potential_armor_key}.png) é fallback. Usando sprite base.")
                else: # Se nem existe a chave no SPRITES (não deveria acontecer se create_sprites_and_tiles rodou)
                     print(f"AVISO: Sprite para armadura '{self.equipped_armor_id}' ({potential_armor_key}.png) não carregado. Usando sprite base.")
        
        if SPRITES.get(target_sprite_key):
            self.image = SPRITES[target_sprite_key]
        else:
            # Fallback crítico se nem o sprite base estiver disponível
            print(f"ERRO CRÍTICO: Sprite '{target_sprite_key}' não encontrado em SPRITES. Usando fallback de emergência.")
            self.image = pygame.Surface(VAMPIRE_SIZE, pygame.SRCALPHA); self.image.fill(DARK_RED)
        
        current_center = self.rect.center 
        self.rect = self.image.get_rect(center=current_center) 
        self.image_key = target_sprite_key 

    def _update_stats_from_level_and_armor(self):
        self.max_hp_base = VAMPIRE_START_HP + (self.level - 1) * VAMPIRE_HP_PER_LEVEL
        current_max_hp = self.max_hp_base
        current_damage = self.base_projectile_damage

        if self.equipped_armor_id and self.equipped_armor_id in ARMORS_DATA:
            armor_stats = ARMORS_DATA[self.equipped_armor_id]
            current_max_hp += armor_stats['hp_bonus']
            current_damage += armor_stats['damage_bonus']

        self.max_hp = current_max_hp
        self.current_projectile_damage = current_damage
        
        if self.hp > self.max_hp: self.hp = self.max_hp
        
        self.shoot_cooldown = max(MIN_SHOOT_COOLDOWN, BASE_SHOOT_COOLDOWN - self.vampiric_strength * COOLDOWN_REDUCTION_PER_STRENGTH)
        self.update_title()

    def update(self, keys, game_state_ref):
        dx, dy = 0,0
        if keys[pygame.K_w]: dy -=1
        if keys[pygame.K_s]: dy +=1
        if keys[pygame.K_a]: dx -=1
        if keys[pygame.K_d]: dx +=1
        if dx != 0 or dy != 0:
            self.direction = pygame.Vector2(dx,dy).normalize()
            self.last_moved_direction = self.direction
            self.rect.x += self.speed * self.direction.x
            self.rect.y += self.speed * self.direction.y
        self.rect.clamp_ip(screen.get_rect())
        
        if game_state_ref.current_map == "castle" and self.hp < self.max_hp: 
            self.hp = min(self.max_hp, self.hp + 0.05)

    def gain_exp(self, amount):
        self.exp += amount
        exp_to_next = EXP_TO_LEVEL_UP_BASE * self.level
        leveled_up = False
        while self.exp >= exp_to_next:
            self.exp -= exp_to_next; self.level += 1; leveled_up = True
            print(f"Vampire leveled up to {self.level}!")
            exp_to_next = EXP_TO_LEVEL_UP_BASE * self.level
        
        if leveled_up:
            self._update_stats_from_level_and_armor() 
            self.hp = self.max_hp 
            self.check_spell_unlocks()
            self.check_armor_unlocks()

    def update_title(self):
        if self.level < 5: self.title = "Fledgling"
        elif self.level < 10: self.title = "Blood Seeker"
        elif self.level < SPREAD_SHOT_LEVEL * 3 : self.title = "Night Stalker"
        elif self.level < BURST_SHOT_LEVEL * 2: self.title = "Elder Vampire"
        else: self.title = "Vampire Lord"

    def increase_vampiric_strength(self, amount=1):
        self.vampiric_strength += amount
        self._update_stats_from_level_and_armor() 

    def shoot(self):
        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_shot_time > self.shoot_cooldown:
            self.last_shot_time = curr_time; projs = []
            shoot_dir = -self.last_moved_direction.normalize() if self.last_moved_direction.length_squared() > 0 else pygame.Vector2(-1,0)
            proj_dmg = self.current_projectile_damage

            if self.level >= BURST_SHOT_LEVEL:
                for i in range(12): projs.append(Projectile(self.rect.center, pygame.Vector2(1,0).rotate(i*30), 'projectile', PROJECTILE_SPEED, damage=proj_dmg))
            elif self.level >= SPREAD_SHOT_LEVEL:
                projs.append(Projectile(self.rect.center, shoot_dir, 'projectile', PROJECTILE_SPEED, damage=proj_dmg))
                projs.append(Projectile(self.rect.center, shoot_dir.rotate(25), 'projectile', PROJECTILE_SPEED, damage=proj_dmg))
                projs.append(Projectile(self.rect.center, shoot_dir.rotate(-25), 'projectile', PROJECTILE_SPEED, damage=proj_dmg))
            else: projs.append(Projectile(self.rect.center, shoot_dir, 'projectile', PROJECTILE_SPEED, damage=proj_dmg))
            return projs
        return []

    def check_spell_unlocks(self):
        for spell_id, data in SPELLS_DATA.items():
            if spell_id not in self.spells and self.level >= data['unlock_level']:
                self.spells[spell_id] = {'unlocked':True, 'last_used':0, 'data':data}; print(f"Spell Unlocked: {data['name']}")
    
    def check_armor_unlocks(self):
        for armor_id, data in ARMORS_DATA.items():
            if armor_id not in self.unlocked_armors and self.level >= data['unlock_level']:
                self.unlocked_armors.add(armor_id)
                print(f"Armor Unlocked: {data['name']}")

    def equip_spell(self, spell_id):
        if spell_id in self.spells and self.spells[spell_id]['unlocked']: self.equipped_spell_id = spell_id; print(f"Equipped Spell: {self.spells[spell_id]['data']['name']}")
        elif spell_id is None: self.equipped_spell_id = None; print("Spells unequipped")
        else: print(f"Cannot equip spell {spell_id}")

    def equip_armor(self, armor_id):
        changed_armor = False
        if armor_id is None: 
            if self.equipped_armor_id is not None: # Só muda se havia uma armadura equipada
                # print(f"Unequipped armor: {ARMORS_DATA[self.equipped_armor_id]['name']}")
                self.equipped_armor_id = None
                changed_armor = True
        elif armor_id in self.unlocked_armors:
            if self.equipped_armor_id != armor_id: # Só muda se for uma armadura diferente
                self.equipped_armor_id = armor_id
                # print(f"Equipped armor: {ARMORS_DATA[armor_id]['name']}")
                changed_armor = True
        else:
            # print(f"Cannot equip armor {armor_id}. Not unlocked or doesn't exist.")
            return # Não faz nada se a armadura não pode ser equipada

        if changed_armor:
            print(f"Armor changed. New equipped_armor_id: {self.equipped_armor_id}")
            self._update_stats_from_level_and_armor() 
            self._set_image_based_on_armor()          

    def use_equipped_spell(self):
        if not self.equipped_spell_id: return None
        spell = self.spells[self.equipped_spell_id]; curr_time = pygame.time.get_ticks()
        if curr_time - spell['last_used'] > spell['data']['cooldown']:
            spell['last_used'] = curr_time
            cast_dir = self.last_moved_direction if self.last_moved_direction.length_squared() > 0 else pygame.Vector2(1,0)
            return spell['data']['activate_func'](self, cast_dir) 
        return None

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0: self.hp = 0; return True
        return False

class Human(GameObject):
    def __init__(self, pos): super().__init__('human_alive', pos); self.sucked = False
    def get_sucked(self):
        if not self.sucked: self.sucked = True; self.image = SPRITES.get('human_dead', self.image)

class Projectile(GameObject):
    def __init__(self, pos, direction, image_key='projectile', speed=PROJECTILE_SPEED, damage=10, lifetime=2000): 
        super().__init__(image_key, pos)
        self.velocity = direction.normalize() * speed if direction.length_squared() > 0 else pygame.Vector2(0,-1)*speed
        self.damage = damage 
        self.spawn_time = pygame.time.get_ticks(); self.lifetime = lifetime
    def update(self):
        self.rect.move_ip(self.velocity.x, self.velocity.y)
        if not screen.get_rect().colliderect(self.rect) or pygame.time.get_ticks() - self.spawn_time > self.lifetime: self.kill()

class BloodBombExplosion(GameObject):
    def __init__(self, pos):
        super().__init__('__blood_explosion_placeholder__', pos) 
        self.image = pygame.Surface((80,80), pygame.SRCALPHA); pygame.draw.circle(self.image, ORANGE, (40,40),40); pygame.draw.circle(self.image, RED, (40,40),30)
        self.rect = self.image.get_rect(center=pos); self.damage = 30; self.spawn_time = pygame.time.get_ticks(); self.duration = 300
    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.duration: self.kill()

class BloodBombProjectile(Projectile):
    def __init__(self, pos, direction_vector):
        super().__init__(pos, direction_vector, 'blood_bomb_projectile', speed=7, damage=0, lifetime=1000)
        self.exploded = False
    def update(self):
        super().update()
        if not self.alive() and not self.exploded:
            self.exploded = True
            if 'game_state' in globals() and game_state: game_state.add_effect(BloodBombExplosion(self.rect.center))

def activate_blood_bomb(caster, caster_direction): return [BloodBombProjectile(caster.rect.center, caster_direction)]
def activate_night_beam(caster, caster_direction): 
    beam_damage = caster.current_projectile_damage + 15 
    return [Projectile(caster.rect.center, caster_direction, 'night_beam_projectile', 20, beam_damage, 500)]

SPELLS_DATA = {
    'blood_bomb': {'name':"Blood Bomb", 'unlock_level':3, 'cooldown':8000, 'activate_func':activate_blood_bomb, 'key_to_equip':pygame.K_1},
    'night_beam': {'name':"Night Beam", 'unlock_level':6, 'cooldown':5000, 'activate_func':activate_night_beam, 'key_to_equip':pygame.K_2},
}

class GameState:
    def __init__(self):
        pygame.display.set_caption("Vampire Legacy - Armored Skins v2") 
        self.clock = pygame.time.Clock()
        self.vampire = None
        self.humans = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group() 
        self.current_map = "castle"
        self.current_stage = 0
        self.last_hunt_stage = 0
        self.active_hunt_data = None 
        self.game_over_flag = False; self.restart_timer = 0; self.paused = False
        self.show_save_load_message_timer = 0; self.save_load_message_text = ""
        
        # create_sprites_and_tiles() deve ser chamado antes de setup_game se setup_game pode criar um vampiro
        if not SPRITES: create_sprites_and_tiles()
        self.setup_game()

    def setup_game(self, from_load=False):
        if not SPRITES: create_sprites_and_tiles() # Garante sprites se setup_game for chamado diretamente

        if not from_load:
            # Se o vampiro já existe (ex: restart), remove-o dos grupos antes de criar um novo
            if self.vampire: self.vampire.kill()
            self.vampire = Vampire((WIDTH // 2, HEIGHT // 2))
            self.current_stage = 0
            self.last_hunt_stage = 0
            self.active_hunt_data = None
            # Atributos resetados no Vampire.__init__ e chamadas subsequentes
            self.vampire.hp = self.vampire.max_hp
            self.vampire.exp = 0; self.vampire.level = 1; self.vampire.vampiric_strength = 0
            self.vampire.equipped_spell_id = None; self.vampire.spells = {}
            self.vampire.equipped_armor_id = None; self.vampire.unlocked_armors = set()
            self.vampire._update_stats_from_level_and_armor()
            self.vampire._set_image_based_on_armor()

        self.all_sprites.empty()
        self.humans.empty()
        self.enemies.empty()
        self.projectiles.empty()
        self.effects.empty()

        if self.vampire:
            self.all_sprites.add(self.vampire) 
            # As verificações de unlock e atualizações de stats/imagem já são feitas
            # no __init__ do Vampire ou no bloco `from_load=False` acima,
            # e no `load_game` para `from_load=True`.
            # No entanto, uma chamada aqui pode garantir consistência se from_load=True e o vampiro já existe.
            self.vampire.check_spell_unlocks() 
            self.vampire.check_armor_unlocks()
            self.vampire._update_stats_from_level_and_armor() 
            self.vampire._set_image_based_on_armor()

        self.game_over_flag = False; self.paused = False; self.restart_timer = 0
        
        if not from_load:
            self.change_map("castle") 
        else:
            self.change_map(self.current_map)


    def change_map(self, new_map_name):
        previous_map = self.current_map
        self.projectiles.empty(); self.effects.empty()
        for p in list(self.all_sprites): 
            if isinstance(p, (Projectile, BloodBombExplosion)): p.kill()

        if "hunt" in previous_map and new_map_name == "castle":
            if self.vampire: # Garante que temos vampiro antes de acessar current_stage
                print(f"Pausing hunt on '{previous_map}' (Stage {self.current_stage}). Storing entities.")
                self.active_hunt_data = {
                    'map_name': previous_map, 'stage': self.current_stage,
                    'humans': list(self.humans), 'enemies': list(self.enemies)
                }
            else: # Deve ser raro, mas para segurança
                self.active_hunt_data = None
            for human_sprite in list(self.humans): human_sprite.remove(self.all_sprites) # Mais seguro iterar cópia
            for enemy_sprite in list(self.enemies): enemy_sprite.remove(self.all_sprites)
            self.humans.empty(); self.enemies.empty()
            self.current_map = "castle"; self.current_stage = 0
        elif previous_map == "castle" and "hunt" in new_map_name:
            if self.active_hunt_data and self.active_hunt_data['map_name'] == new_map_name:
                print(f"Resuming hunt on '{new_map_name}' (Stage {self.active_hunt_data['stage']}). Restoring entities.")
                self.current_map = self.active_hunt_data['map_name']; self.current_stage = self.active_hunt_data['stage']
                self.humans.empty(); self.enemies.empty()
                for human_sprite in self.active_hunt_data['humans']: self.humans.add(human_sprite); self.all_sprites.add(human_sprite)
                for enemy_sprite in self.active_hunt_data['enemies']: self.enemies.add(enemy_sprite); self.all_sprites.add(enemy_sprite)
                self.active_hunt_data = None
            else:
                if self.active_hunt_data:
                    print(f"Discarding paused state for '{self.active_hunt_data['map_name']}' to start new hunt on '{new_map_name}'.")
                    self.active_hunt_data = None
                print(f"Starting new/fresh hunt on '{new_map_name}'.")
                self.current_map = new_map_name
                self.current_stage = self.last_hunt_stage + 1 if self.last_hunt_stage > 0 else 1
                self.humans.empty(); self.enemies.empty()
                self.start_new_stage()
        elif "hunt" in previous_map and "hunt" in new_map_name and previous_map != new_map_name:
            print(f"Switching from hunt '{previous_map}' to new hunt '{new_map_name}'. Previous hunt state discarded.")
            self.active_hunt_data = None
            for h_sprite in list(self.humans): h_sprite.remove(self.all_sprites)
            for e_sprite in list(self.enemies): e_sprite.remove(self.all_sprites)
            self.humans.empty(); self.enemies.empty()
            self.current_map = new_map_name
            self.current_stage = self.last_hunt_stage + 1 if self.last_hunt_stage > 0 else 1
            self.start_new_stage()
        else: 
            self.current_map = new_map_name
            if self.current_map == "castle":
                self.current_stage = 0
                if self.active_hunt_data: 
                    for h_sprite in list(self.active_hunt_data['humans']): h_sprite.remove(self.all_sprites)
                    for e_sprite in list(self.active_hunt_data['enemies']): e_sprite.remove(self.all_sprites)
                    self.active_hunt_data = None
                for h_sprite in list(self.humans): h_sprite.remove(self.all_sprites) 
                for e_sprite in list(self.enemies): e_sprite.remove(self.all_sprites)
                self.humans.empty(); self.enemies.empty()
            elif "hunt" in self.current_map and not self.active_hunt_data : 
                 self.humans.empty(); self.enemies.empty()
                 self.current_stage = self.last_hunt_stage + 1 if self.last_hunt_stage > 0 else 1
                 self.start_new_stage()
        
        print(f"Changed map to: {self.current_map}. Stage: {self.current_stage}")

    def start_new_stage(self):
        self.active_hunt_data = None 
        if self.current_stage == 0: self.current_stage = 1 
        print(f"--- Generating entities for Stage {self.current_stage} on map {self.current_map} ---")
        for h_sprite in list(self.humans): h_sprite.kill()
        for e_sprite in list(self.enemies): e_sprite.kill()

        num_humans = BASE_HUMANS_PER_STAGE + (self.current_stage - 1) * HUMANS_INCREMENT_PER_STAGE
        total_enemies = BASE_ENEMIES_PER_STAGE + (self.current_stage - 1) * ENEMIES_INCREMENT_PER_STAGE
        speed_mult = 1.0 + (self.current_stage - 1) * (ENEMY_SPEED_INCREMENT_PER_STAGE / ENEMY_BASE_SPEED)

        for _ in range(num_humans):
            h_pos = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
            human = Human(h_pos); self.humans.add(human); self.all_sprites.add(human)
        
        for _ in range(total_enemies):
            e_pos_choice = (random.choice([random.randint(0,50), random.randint(WIDTH-50,WIDTH)]),
                            random.choice([random.randint(0,50), random.randint(HEIGHT-50,HEIGHT)]))
            EnemyClass = random.choice(ENEMY_TYPES)
            enemy = EnemyClass(e_pos_choice, speed_mult)
            if self.vampire: 
                v_rect_inf = self.vampire.rect.inflate(150,150)
                while enemy.rect.colliderect(v_rect_inf):
                    enemy.rect.center = (random.choice([random.randint(0,50), random.randint(WIDTH-50,WIDTH)]),
                                         random.choice([random.randint(0,50), random.randint(HEIGHT-50,HEIGHT)]))
            self.enemies.add(enemy); self.all_sprites.add(enemy)
        
        print(f"Generated stage {self.current_stage}: {len(self.humans)} humans, {len(self.enemies)} enemies.")

    def add_projectile(self, proj_or_list): 
        if proj_or_list:
            items = proj_or_list if isinstance(proj_or_list, list) else [proj_or_list]
            for item in items:
                if item: self.projectiles.add(item); self.all_sprites.add(item)
    def add_effect(self, effect): 
        if effect: self.effects.add(effect); self.all_sprites.add(effect)

    def save_game(self): 
        if not self.vampire: return False
        stage_to_save_as_last = self.last_hunt_stage
        if self.current_map != "castle": stage_to_save_as_last = self.current_stage
        elif self.active_hunt_data: stage_to_save_as_last = self.active_hunt_data['stage']
        
        data = {
            'vampire': {'hp':self.vampire.hp, 'max_hp':self.vampire.max_hp, 
                        'max_hp_base': self.vampire.max_hp_base,
                        'exp':self.vampire.exp, 'level':self.vampire.level,
                        'vampiric_strength':self.vampire.vampiric_strength, 
                        'equipped_spell_id':self.vampire.equipped_spell_id,
                        'spells_unlocked':[sid for sid,d in self.vampire.spells.items() if d['unlocked']],
                        'pos':list(self.vampire.rect.center),
                        'equipped_armor_id': self.vampire.equipped_armor_id, # Salva ID da armadura
                        'unlocked_armors': list(self.vampire.unlocked_armors)},
            'game_state': {'current_map':"castle", 
                           'last_hunt_stage': stage_to_save_as_last }
        }
        try:
            with open(SAVE_FILENAME, 'w') as f: json.dump(data, f, indent=4)
            self.save_load_message_text = "Game Saved!"; self.show_save_load_message_timer = pygame.time.get_ticks() + 2000
        except IOError as e: print(f"Save error: {e}"); self.save_load_message_text = "Error Saving!"; self.show_save_load_message_timer = pygame.time.get_ticks() + 2000

    def load_game(self): 
        try:
            with open(SAVE_FILENAME, 'r') as f: loaded = json.load(f)
            
            if not SPRITES: create_sprites_and_tiles()

            if self.vampire: self.vampire.kill() 
            
            v_data_for_pos = loaded['vampire']
            initial_pos = tuple(v_data_for_pos.get('pos', (WIDTH // 2, HEIGHT // 2)))
            self.vampire = Vampire(initial_pos) # Cria novo vampiro. __init__ define sprite base.
            
            v_data = loaded['vampire']
            self.vampire.hp=v_data['hp']
            self.vampire.max_hp_base = v_data.get('max_hp_base', VAMPIRE_START_HP + (v_data['level']-1)*VAMPIRE_HP_PER_LEVEL) 
            self.vampire.exp=v_data['exp']; self.vampire.level=v_data['level']
            self.vampire.vampiric_strength=v_data['vampiric_strength']
            self.vampire.equipped_spell_id=v_data['equipped_spell_id']
            
            self.vampire.spells = {}
            for sid in v_data.get('spells_unlocked',[]):
                if sid in SPELLS_DATA: self.vampire.spells[sid] = {'unlocked':True, 'last_used':0, 'data':SPELLS_DATA[sid]}
            
            self.vampire.unlocked_armors = set(v_data.get('unlocked_armors', []))
            self.vampire.equipped_armor_id = v_data.get('equipped_armor_id', None) # Carrega ID da armadura

            # ESSENCIAL: Atualizar stats e imagem APÓS carregar todos os dados do vampiro
            self.vampire._update_stats_from_level_and_armor() 
            self.vampire._set_image_based_on_armor() # Define o sprite correto
            
            self.vampire.hp = min(self.vampire.hp, self.vampire.max_hp) # Garante HP válido

            gs_data = loaded['game_state']
            self.last_hunt_stage = gs_data.get('last_hunt_stage', 0)
            self.current_map = "castle" 
            self.current_stage = 0      
            self.active_hunt_data = None 

            self.setup_game(from_load=True) # Finaliza configuração, adiciona vampiro a all_sprites, etc.
            self.save_load_message_text = "Game Loaded!"; self.show_save_load_message_timer = pygame.time.get_ticks() + 2000
        except FileNotFoundError: 
            self.save_load_message_text = "No Save File."; self.show_save_load_message_timer = pygame.time.get_ticks() + 2000
            # Se não há save, garante um setup limpo se o jogo acabou de iniciar
            if not self.vampire: self.setup_game() 
            elif not SPRITES: create_sprites_and_tiles(); self.vampire._set_image_based_on_armor() # Garante sprites
        except (IOError, json.JSONDecodeError, KeyError) as e:
            print(f"Load error: {e}"); self.save_load_message_text = "Error Loading! Resetting."; self.show_save_load_message_timer = pygame.time.get_ticks() + 3000
            self.setup_game() # Reseta para um estado limpo


    def handle_input(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if self.game_over_flag:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.setup_game()
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.paused = not self.paused
                if self.paused and event.key != pygame.K_ESCAPE: continue

                if self.current_map == "castle" and self.vampire:
                    if event.key == pygame.K_F5: self.save_game()
                    elif event.key == pygame.K_F9: self.load_game()
                    
                    # Equipar magias
                    for sid, data in SPELLS_DATA.items():
                        if event.key == data['key_to_equip']: self.vampire.equip_spell(sid); break
                    if event.key == pygame.K_0: self.vampire.equip_spell(None)
                    
                    # Equipar armaduras
                    for armor_id, data in ARMORS_DATA.items():
                        if event.key == data['key_to_equip']: self.vampire.equip_armor(armor_id); break
                    if event.key == ARMOR_UNEQUIP_KEY: self.vampire.equip_armor(None)


                if event.key == pygame.K_F1 and self.current_map != "castle": self.change_map("castle")
                elif event.key == pygame.K_F2 and self.current_map != "hunt_forest": self.change_map("hunt_forest")
                elif event.key == pygame.K_F3 and self.current_map != "hunt_village": self.change_map("hunt_village")

                if not self.paused and self.vampire: 
                    if event.key == pygame.K_SPACE: self.add_projectile(self.vampire.shoot())
                    if event.key == pygame.K_f:
                        spell_sprites = self.vampire.use_equipped_spell()
                        if spell_sprites: 
                            for item in spell_sprites: 
                                if isinstance(item, Projectile): self.add_projectile(item) 
                                else: self.add_effect(item) 
        if not self.game_over_flag and not self.paused and self.vampire: self.vampire.update(keys, self)
        return True

    def update_game_logic(self): 
        if self.game_over_flag or self.paused or not self.vampire: return

        if self.current_map != "castle":
            for enemy in list(self.enemies): 
                enemy.update(self.vampire.rect.center)
                if self.vampire.rect.colliderect(enemy.rect):
                    if self.vampire.take_damage(enemy.damage_to_vampire):
                        self.game_over_flag = True; self.restart_timer = pygame.time.get_ticks() + 5000
                        print("Vampire Died!")
                        break 
                    else: 
                        push = pygame.Vector2(enemy.rect.center)-pygame.Vector2(self.vampire.rect.center)
                        if push.length_squared()>0: enemy.rect.move_ip(push.normalize()*5)
                        else: enemy.rect.x += 10 # Evita ficar preso
            if self.game_over_flag: return 
            
            for human in pygame.sprite.spritecollide(self.vampire, self.humans, False):
                if not human.sucked:
                    human.get_sucked(); self.vampire.gain_exp(EXP_PER_HUMAN)
                    self.vampire.increase_vampiric_strength(); self.vampire.hp = min(self.vampire.max_hp, self.vampire.hp+5)
            
            if "hunt" in self.current_map and self.current_stage > 0:
                all_sucked = all(h.sucked for h in self.humans) if self.humans else True
                if all_sucked and not self.enemies: 
                    print(f"Stage {self.current_stage} on map '{self.current_map}' Clear! Advancing.")
                    self.last_hunt_stage = self.current_stage 
                    self.current_stage += 1 
                    self.start_new_stage() 

        self.projectiles.update()
        self.effects.update()

        for proj in list(self.projectiles):
            if not isinstance(proj, BloodBombProjectile) and hasattr(proj, 'damage') and proj.damage > 0:
                hit_enemies = pygame.sprite.spritecollide(proj, self.enemies, False) 
                for e_hit in hit_enemies:
                    if e_hit.take_damage(proj.damage): self.vampire.gain_exp(e_hit.exp_value)
                    proj.kill(); break 
        
        for effect in list(self.effects):
            if isinstance(effect, BloodBombExplosion):
                exploded_enemies = pygame.sprite.spritecollide(effect, self.enemies, False)
                for e_hit in exploded_enemies:
                    if e_hit.take_damage(effect.damage): self.vampire.gain_exp(e_hit.exp_value * 1.5)
    
    def draw_hud(self): 
        if not self.vampire: return
        hp_s = FONT_SMALL.render(f"HP: {int(self.vampire.hp)}/{self.vampire.max_hp}",1,WHITE)
        lvl_s = FONT_SMALL.render(f"Lvl: {self.vampire.level} ({self.vampire.exp}/{EXP_TO_LEVEL_UP_BASE*self.vampire.level})",1,WHITE)
        tit_s = FONT_SMALL.render(f"Title: {self.vampire.title}",1,WHITE)
        str_s = FONT_SMALL.render(f"Str: {self.vampire.vampiric_strength}",1,WHITE)
        dmg_s = FONT_SMALL.render(f"Atk: {self.vampire.current_projectile_damage}", 1, WHITE)
        screen.blit(hp_s,(10,10)); screen.blit(lvl_s,(10,30)); screen.blit(tit_s,(10,50)); screen.blit(str_s,(10,70)); screen.blit(dmg_s, (10,90))

        map_s = FONT_SMALL.render(f"Map: {self.current_map.replace('_',' ').title()}",1,WHITE)
        screen.blit(map_s, (WIDTH-map_s.get_width()-10,10))

        info_y_offset = 30
        if self.current_map == "castle":
            if self.active_hunt_data:
                paused_info = f"Paused: {self.active_hunt_data['map_name'].replace('_',' ').title()} (Stg {self.active_hunt_data['stage']})"
                paused_s = FONT_SMALL.render(paused_info, 1, ORANGE)
                screen.blit(paused_s, (WIDTH - paused_s.get_width() - 10, info_y_offset)); info_y_offset += 20
            if self.last_hunt_stage > 0 :
                last_stg_s = FONT_SMALL.render(f"Max Hunt Stg: {self.last_hunt_stage}", 1, YELLOW)
                screen.blit(last_stg_s, (WIDTH - last_stg_s.get_width() - 10, info_y_offset))
        elif "hunt" in self.current_map:
            stg_s = FONT_SMALL.render(f"Stage: {self.current_stage}",1,WHITE)
            screen.blit(stg_s, (WIDTH-stg_s.get_width()-10,info_y_offset)); info_y_offset +=20
            h_left = sum(1 for h in self.humans if not h.sucked)
            h_s = FONT_SMALL.render(f"Humans: {h_left}",1,WHITE if h_left > 0 else YELLOW)
            screen.blit(h_s, (WIDTH-h_s.get_width()-10,info_y_offset)); info_y_offset +=20
            e_s = FONT_SMALL.render(f"Enemies: {len(self.enemies)}",1,WHITE if self.enemies else YELLOW)
            screen.blit(e_s, (WIDTH-e_s.get_width()-10,info_y_offset))

        bottom_hud_y = HEIGHT - 30
        if self.vampire.equipped_armor_id and self.vampire.equipped_armor_id in ARMORS_DATA:
            armor_name = ARMORS_DATA[self.vampire.equipped_armor_id]['name']
            armor_s = FONT_SMALL.render(f"Armor: {armor_name}", 1, WHITE)
            screen.blit(armor_s, (10, bottom_hud_y))
            bottom_hud_y -= 20 
        elif self.vampire.equipped_armor_id is None: # Mostra "No Armor" se nada estiver equipado
            armor_s = FONT_SMALL.render(f"Armor: None", 1, GRAY)
            screen.blit(armor_s, (10, bottom_hud_y))
            bottom_hud_y -= 20


        if self.vampire.equipped_spell_id and self.vampire.equipped_spell_id in self.vampire.spells:
            s_info = self.vampire.spells[self.vampire.equipped_spell_id]; s_name = s_info['data']['name']
            s_cd_rem = max(0, s_info['data']['cooldown']-(pygame.time.get_ticks()-s_info['last_used']))
            s_stat = f"Spell: {s_name}" + (f" (CD: {s_cd_rem/1000:.1f}s)" if s_cd_rem > 0 else " (Ready!)")
            spell_s = FONT_SMALL.render(s_stat,1,WHITE); screen.blit(spell_s, (10, bottom_hud_y))
        
        if self.current_map == "castle":
            y_off = HEIGHT - 170 # Ajustado para mais espaço para armaduras
            screen.blit(FONT_SMALL.render("[F1]Castle [F2]Forest [F3]Village",1,YELLOW),(10,y_off)); y_off+=20
            screen.blit(FONT_SMALL.render("[F5]Save | [F9]Load",1,YELLOW),(10,y_off)); y_off+=20
            
            screen.blit(FONT_SMALL.render("Spells ([0] Unequip):", 1, YELLOW), (10, y_off)); y_off += 20
            for sid, s_data_dict in self.vampire.spells.items():
                if s_data_dict['unlocked']:
                    key_c = pygame.key.name(SPELLS_DATA[sid]['key_to_equip']).upper()
                    s_t = f"  [{key_c}] {s_data_dict['data']['name']}" + (" (EQUIPPED)" if self.vampire.equipped_spell_id==sid else "")
                    screen.blit(FONT_SMALL.render(s_t,1,GREEN if self.vampire.equipped_spell_id==sid else WHITE),(10,y_off)); y_off+=20
            
            y_off += 5 
            unequip_armor_key_name = pygame.key.name(ARMOR_UNEQUIP_KEY).upper()
            screen.blit(FONT_SMALL.render(f"Armors ([{unequip_armor_key_name}] Unequip):", 1, YELLOW), (10, y_off)); y_off += 20
            for aid, a_data in ARMORS_DATA.items(): # Itera sobre as armaduras definidas
                if aid in self.vampire.unlocked_armors:
                    key_c = pygame.key.name(a_data['key_to_equip']).upper()
                    a_t = f"  [{key_c}] {a_data['name']} (HP+{a_data['hp_bonus']}, Atk+{a_data['damage_bonus']})"
                    a_t += (" (EQUIPPED)" if self.vampire.equipped_armor_id == aid else "")
                    screen.blit(FONT_SMALL.render(a_t, 1, GREEN if self.vampire.equipped_armor_id == aid else WHITE), (10, y_off)); y_off += 20
        
        if self.show_save_load_message_timer > pygame.time.get_ticks():
            msg_s = FONT_MEDIUM.render(self.save_load_message_text,1,YELLOW)
            screen.blit(msg_s, msg_s.get_rect(center=(WIDTH//2, HEIGHT-50)))
        elif self.show_save_load_message_timer != 0: self.show_save_load_message_timer = 0

    def draw_elements(self): 
        if "hunt" in self.current_map:
            if GRASS_TILE_IMG:
                tw,th = GRASS_TILE_IMG.get_size()
                for x in range(0,WIDTH,tw):
                    for y in range(0,HEIGHT,th): screen.blit(GRASS_TILE_IMG,(x,y))
            else: screen.fill(GREEN) 
        elif self.current_map == "castle": screen.fill(BLACK)
        else: screen.fill(GRAY) 
        
        self.all_sprites.draw(screen) 
        self.draw_hud()

        if self.game_over_flag:
            over = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); over.fill((0,0,0,180)); screen.blit(over,(0,0))
            go_s = FONT_LARGE.render("VOCÊ MORREU!",1,RED); screen.blit(go_s,go_s.get_rect(center=(WIDTH//2,HEIGHT//2-30)))
            msg = "Pressione 'R' para reiniciar"
            if self.restart_timer > 0 and pygame.time.get_ticks() < self.restart_timer: msg = f"Reiniciando em {(self.restart_timer-pygame.time.get_ticks())//1000}s... ou 'R'"
            elif self.restart_timer > 0 and pygame.time.get_ticks() >= self.restart_timer: self.setup_game(); return 
            rs_s = FONT_MEDIUM.render(msg,1,WHITE); screen.blit(rs_s,rs_s.get_rect(center=(WIDTH//2,HEIGHT//2+20)))
        
        if self.paused:
            over = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); over.fill((0,0,0,150)); screen.blit(over,(0,0))
            p_s = FONT_LARGE.render("PAUSADO",1,YELLOW); screen.blit(p_s,p_s.get_rect(center=(WIDTH//2,HEIGHT//2)))
        
        pygame.display.flip()

    def run(self): 
        running = True
        while running:
            self.clock.tick(FPS)
            if not self.handle_input(): running=False; break 
            if not (self.game_over_flag and self.restart_timer > 0 and pygame.time.get_ticks() >= self.restart_timer):
                self.update_game_logic()
                self.draw_elements()
        pygame.quit()

# === PONTO DE ENTRADA ===
if __name__ == '__main__':
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    game_state = GameState() 
    game_state.run()
