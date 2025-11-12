import pygame
import random
import math
import os
import json # <<< ADICIONADO

pygame.init()
pygame.font.init()

# === CONSTANTES ===
WIDTH, HEIGHT = 800, 600
FPS = 60

# Cores (ainda úteis)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
DARK_RED = (100, 0, 0)
SKIN = (255, 220, 200)
PURPLE = (138, 43, 226) # Cor base para inimigo original
BLUE = (0, 100, 255)
GRAY = (180, 180, 180)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GREEN_DARK = (0, 100, 0) # Para Ghoul
BROWN = (139, 69, 19) # Para Bat (corpo)
BONE_WHITE = (245, 245, 220) # Para Skeleton
GREEN = (50, 168, 82)

# Configurações do Jogo
VAMPIRE_START_HP = 100
VAMPIRE_SPEED = 5
PROJECTILE_SPEED = 10
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
SAVE_FILENAME = "savegame.json" # <<< ADICIONADO

# --- Tamanhos dos sprites ---
VAMPIRE_SIZE = (60, 60)
HUMAN_SIZE = (40, 40)
ENEMY_DEFAULT_SIZE = (100, 100)
ENEMY_SLIME_SIZE = (100, 100)
ENEMY_GHOUL_SIZE = (100, 100)
ENEMY_BAT_SIZE = (100, 100)
ENEMY_SKELETON_SIZE = (100, 100)

PROJECTILE_SIZE_NORMAL = (15, 15)
PROJECTILE_SIZE_BLOODBOMB = (25, 25)
PROJECTILE_SIZE_NIGHTBEAM = (80, 15)

# === ASSETS GLOBAIS ===
SPRITES = {}
GRASS_TILE_IMG = None

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
    global GRASS_TILE_IMG

    SPRITES['vampire'] = load_image(os.path.join(SPRITE_PATH, "vampire.png"), VAMPIRE_SIZE)
    SPRITES['human_alive'] = load_image(os.path.join(SPRITE_PATH, "human_alive.png"), HUMAN_SIZE)
    SPRITES['human_dead'] = load_image(os.path.join(SPRITE_PATH, "human_dead.png"), HUMAN_SIZE)

    SPRITES['enemy_slime'] = load_image(os.path.join(SPRITE_PATH, "enemy_slime.png"), ENEMY_SLIME_SIZE)
    SPRITES['enemy_ghoul'] = load_image(os.path.join(SPRITE_PATH, "enemy_ghoul.png"), ENEMY_GHOUL_SIZE)
    SPRITES['enemy_bat'] = load_image(os.path.join(SPRITE_PATH, "enemy_bat.png"), ENEMY_BAT_SIZE)
    SPRITES['enemy_skeleton'] = load_image(os.path.join(SPRITE_PATH, "enemy_skeleton.png"), ENEMY_SKELETON_SIZE)

    SPRITES['projectile'] = load_image(os.path.join(SPRITE_PATH, "projectile.png"), PROJECTILE_SIZE_NORMAL)
    SPRITES['blood_bomb_projectile'] = load_image(os.path.join(SPRITE_PATH, "blood_bomb_projectile.png"), PROJECTILE_SIZE_BLOODBOMB)
    SPRITES['night_beam_projectile'] = load_image(os.path.join(SPRITE_PATH, "night_beam_projectile.png"), PROJECTILE_SIZE_NIGHTBEAM)

    if not SPRITES.get('enemy_slime') or (SPRITES['enemy_slime'] and SPRITES['enemy_slime'].get_at((0,0))[:3] == (255,0,255)):
        e_surface = pygame.Surface(ENEMY_SLIME_SIZE, pygame.SRCALPHA)
        pygame.draw.ellipse(e_surface, PURPLE, e_surface.get_rect())
        pygame.draw.circle(e_surface, RED, (10, 10), 4); pygame.draw.circle(e_surface, RED, (20, 10), 4)
        SPRITES['enemy_slime'] = e_surface
    if not SPRITES.get('enemy_ghoul') or (SPRITES['enemy_ghoul'] and SPRITES['enemy_ghoul'].get_at((0,0))[:3] == (255,0,255)):
        g_surface = pygame.Surface(ENEMY_GHOUL_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(g_surface, GREEN_DARK, (5, 10, 25, 25))
        pygame.draw.circle(g_surface, SKIN, (17, 10), 7)
        SPRITES['enemy_ghoul'] = g_surface
    if not SPRITES.get('enemy_bat') or (SPRITES['enemy_bat'] and SPRITES['enemy_bat'].get_at((0,0))[:3] == (255,0,255)):
        b_surface = pygame.Surface(ENEMY_BAT_SIZE, pygame.SRCALPHA)
        pygame.draw.ellipse(b_surface, BROWN, (2, 5, 26, 20)) # Corpo
        pygame.draw.polygon(b_surface, BLACK, [(0,0), (5,10), (0,20)]) # Asa Esq.
        pygame.draw.polygon(b_surface, BLACK, [(30,0), (25,10), (30,20)]) # Asa Dir.
        SPRITES['enemy_bat'] = b_surface
    if not SPRITES.get('enemy_skeleton') or (SPRITES['enemy_skeleton'] and SPRITES['enemy_skeleton'].get_at((0,0))[:3] == (255,0,255)):
        s_surface = pygame.Surface(ENEMY_SKELETON_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(s_surface, BONE_WHITE, (10, 5, 10, 25)) # Corpo
        pygame.draw.circle(s_surface, BONE_WHITE, (15, 5), 5) # Cabeça
        SPRITES['enemy_skeleton'] = s_surface

    GRASS_TILE_IMG = load_image(os.path.join(SPRITE_PATH, "grass_tile.png"), use_alpha=False)
    if GRASS_TILE_IMG is None: print("Falha ao carregar grass_tile.png. Fundo será cor sólida.")

# === CLASSES ===
class GameObject(pygame.sprite.Sprite):
    def __init__(self, image_key, pos):
        super().__init__()
        self.image_key = image_key
        if image_key in SPRITES and SPRITES[image_key] is not None:
            self.image = SPRITES[image_key]
        else:
            print(f"Aviso: Chave de sprite '{image_key}' não encontrada ou imagem nula. Usando placeholder.")
            self.image = pygame.Surface(ENEMY_DEFAULT_SIZE, pygame.SRCALPHA)
            self.image.fill(PURPLE)
        self.rect = self.image.get_rect(center=pos)

class Enemy(GameObject):
    def __init__(self, image_key, pos, speed, hp=30, exp_value=10, damage_to_vampire=15):
        super().__init__(image_key, pos)
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.exp_value = exp_value
        self.damage_to_vampire = damage_to_vampire

    def update(self, target_pos):
        direction_to_target = pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)
        if direction_to_target.length() > 0:
            direction_to_target = direction_to_target.normalize()
            self.rect.move_ip(direction_to_target * self.speed)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True
        return False

class EnemySlime(Enemy):
    def __init__(self, pos, speed_multiplier=1.0):
        base_speed = ENEMY_BASE_SPEED * speed_multiplier
        super().__init__('enemy_slime', pos, speed=base_speed, hp=30, exp_value=10)

class EnemyGhoul(Enemy):
    def __init__(self, pos, speed_multiplier=0.8):
        base_speed = ENEMY_BASE_SPEED * speed_multiplier
        super().__init__('enemy_ghoul', pos, speed=base_speed, hp=50, exp_value=15, damage_to_vampire=20)

class EnemyBat(Enemy):
    def __init__(self, pos, speed_multiplier=1.5):
        base_speed = ENEMY_BASE_SPEED * speed_multiplier
        super().__init__('enemy_bat', pos, speed=base_speed, hp=20, exp_value=8, damage_to_vampire=10)
        self.move_timer = 0
        self.move_interval = 30
        self.flutter_direction = pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()

    def update(self, target_pos):
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            random_flutter = pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1))
            direction_to_target = pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)
            if direction_to_target.length_squared() > 0:
                self.flutter_direction = (direction_to_target.normalize() * 0.7 + random_flutter.normalize() * 0.3).normalize()
        self.rect.move_ip(self.flutter_direction * self.speed)
        self.rect.clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))

class EnemySkeleton(Enemy):
    def __init__(self, pos, speed_multiplier=0.6):
        base_speed = ENEMY_BASE_SPEED * speed_multiplier
        super().__init__('enemy_skeleton', pos, speed=base_speed, hp=70, exp_value=20, damage_to_vampire=25)

ENEMY_TYPES = [EnemySlime, EnemyGhoul, EnemyBat, EnemySkeleton]

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

    def update(self, keys, game_state_ref):
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
            self.hp += 0.05 # Regeneração lenta no castelo
            if self.hp > self.max_hp: self.hp = self.max_hp

    def gain_exp(self, amount):
        self.exp += amount
        exp_to_next_level = EXP_TO_LEVEL_UP_BASE * self.level
        while self.exp >= exp_to_next_level: # Use while para casos de ganhar múltiplos níveis de uma vez
            self.exp -= exp_to_next_level
            self.level += 1
            self.max_hp += 10
            self.hp = self.max_hp
            print(f"Vampire leveled up to {self.level}!")
            self.check_spell_unlocks()
            exp_to_next_level = EXP_TO_LEVEL_UP_BASE * self.level # Atualiza para o próximo nível

    def update_title(self):
        if self.level < 5: self.title = "Fledgling"
        elif self.level < 10: self.title = "Blood Seeker"
        elif self.level < SPREAD_SHOT_LEVEL * 3 : self.title = "Night Stalker"
        elif self.level < BURST_SHOT_LEVEL * 2: self.title = "Elder Vampire"
        else: self.title = "Vampire Lord"

    def increase_vampiric_strength(self, amount=1):
        self.vampiric_strength += amount
        self.shoot_cooldown = max(MIN_SHOOT_COOLDOWN, BASE_SHOOT_COOLDOWN - self.vampiric_strength * COOLDOWN_REDUCTION_PER_STRENGTH)

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_cooldown:
            self.last_shot_time = current_time
            projectiles_to_add = []
            if self.last_moved_direction.length_squared() > 0:
                 shoot_direction = -self.last_moved_direction.normalize()
            else:
                 shoot_direction = pygame.Vector2(-1, 0) # Padrão se não houver movimento anterior

            if self.level >= BURST_SHOT_LEVEL:
                for i in range(12): # Círculo completo
                    angle = i * (360 / 12)
                    dir_vec = pygame.Vector2(1,0).rotate(angle) # Atira em todas as direções
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
            cast_direction = self.last_moved_direction
            if cast_direction.length_squared() == 0:
                cast_direction = pygame.Vector2(1,0) # Padrão se não houver direção de movimento
            return spell['data']['activate_func'](self, cast_direction)
        return None

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            return True # Vampiro morreu
        return False

class Human(GameObject):
    def __init__(self, pos):
        super().__init__('human_alive', pos)
        self.sucked = False
    def get_sucked(self):
        if not self.sucked:
            self.sucked = True
            self.image = SPRITES.get('human_dead', self.image)

class Projectile(GameObject):
    def __init__(self, pos, direction, image_key='projectile', speed=PROJECTILE_SPEED, damage=10, lifetime=2000):
        super().__init__(image_key, pos)
        if direction.length_squared() > 0:
            self.velocity = direction.normalize() * speed
        else: # Segurança: se a direção for (0,0), atira para cima
            self.velocity = pygame.Vector2(0, -1) * speed
        self.damage = damage
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime
    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        if not screen.get_rect().colliderect(self.rect) or \
           pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

class BloodBombExplosion(GameObject):
    def __init__(self, pos):
        # Placeholder sprite, a imagem real é criada aqui
        super().__init__('__blood_explosion_placeholder__', pos) # Usa uma chave que não precisa estar em SPRITES
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ORANGE, (40, 40), 40)
        pygame.draw.circle(self.image, RED, (40, 40), 30)
        self.rect = self.image.get_rect(center=pos)
        self.damage = 30
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 300 # milissegundos
    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()

class BloodBombProjectile(Projectile):
    def __init__(self, pos, direction_vector):
        super().__init__(pos, direction_vector, 'blood_bomb_projectile', speed=7, damage=0, lifetime=1000)
        self.exploded = False
    def update(self):
        super().update()
        # Verifica se o projétil "morreu" (atingiu a borda ou lifetime expirou) E ainda não explodiu
        if not self.alive() and not self.exploded:
            self.exploded = True
            # Acessa game_state globalmente para adicionar o efeito (pode ser melhorado com passagem de referência)
            if 'game_state' in globals() and game_state:
                game_state.add_effect(BloodBombExplosion(self.rect.center))

# === FUNÇÕES DE MAGIA ===
def activate_blood_bomb(caster, caster_direction):
    return [BloodBombProjectile(caster.rect.center, caster_direction)]
def activate_night_beam(caster, caster_direction):
    # A direção é a direção em que o vampiro está se movendo ou a última direção movida
    return [Projectile(caster.rect.center, caster_direction, 'night_beam_projectile', speed=20, damage=25, lifetime=500)]
def activate_shadow_barrier(caster, caster_direction): # Ainda não implementado funcionalmente
    # Poderia criar um escudo temporário ou algo assim
    print("Shadow Barrier activated (visual only for now)")
    return [] # Não retorna projéteis/efeitos visuais ainda

SPELLS_DATA = {
    'blood_bomb': {'name': "Blood Bomb", 'unlock_level': 3, 'cooldown': 8000, 'activate_func': activate_blood_bomb, 'key_to_equip': pygame.K_1},
    'night_beam': {'name': "Night Beam", 'unlock_level': 6, 'cooldown': 5000, 'activate_func': activate_night_beam, 'key_to_equip': pygame.K_2},
    # 'shadow_barrier': {'name': "Shadow Barrier", 'unlock_level': 9, 'cooldown': 15000, 'activate_func': activate_shadow_barrier, 'key_to_equip': pygame.K_3},
}

# === GERENCIAMENTO DE JOGO ===
class GameState:
    def __init__(self):
        pygame.display.set_caption("Vampire Legacy Evolved - Enhanced")
        self.clock = pygame.time.Clock()
        self.vampire = None
        self.humans = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.current_map = "castle"
        self.current_stage = 0
        self.last_hunt_stage = 0 # <<< MODIFICADO
        self.game_over_flag = False
        self.restart_timer = 0
        self.paused = False
        self.show_save_load_message_timer = 0 # <<< MODIFICADO
        self.save_load_message_text = ""     # <<< MODIFICADO
        self.setup_game()

    def setup_game(self, from_load=False): # <<< MODIFICADO
        if not from_load:
            self.vampire = Vampire((WIDTH // 2, HEIGHT // 2))
            self.current_stage = 0
            self.last_hunt_stage = 0
            # Resetar atributos do vampiro apenas se não for um load
            self.vampire.hp = VAMPIRE_START_HP
            self.vampire.max_hp = VAMPIRE_START_HP
            self.vampire.exp = 0
            self.vampire.level = 1
            self.vampire.vampiric_strength = 0
            self.vampire.equipped_spell_id = None
            self.vampire.spells = {}

        # Estas partes são executadas tanto no setup normal quanto após o load
        self.all_sprites.empty(); self.humans.empty(); self.enemies.empty()
        self.projectiles.empty(); self.effects.empty()

        if self.vampire: # Garante que o vampiro existe
            self.all_sprites.add(self.vampire)
            self.vampire.check_spell_unlocks() # Recheca unlocks com base no nível atual
            self.vampire.update_title()
            # Atualiza o cooldown do tiro com base na força vampírica (importante após load)
            self.vampire.shoot_cooldown = max(MIN_SHOOT_COOLDOWN, BASE_SHOOT_COOLDOWN - self.vampire.vampiric_strength * COOLDOWN_REDUCTION_PER_STRENGTH)

        self.game_over_flag = False
        self.paused = False
        self.restart_timer = 0
        
        if not from_load:
            self.change_map("castle")
        else: # Se for carregamento, apenas atualiza visualização do mapa atual (que será castle)
             self.change_map(self.current_map, preserve_entities=True)


    def change_map(self, map_name, preserve_entities=False): # <<< MODIFICADO
        if "hunt" in self.current_map and map_name == "castle":
            self.last_hunt_stage = self.current_stage # Salva o progresso da caçada
            print(f"Returning to Castle. Last hunt stage was: {self.last_hunt_stage}")

        self.current_map = map_name
        
        if not preserve_entities: # Limpa entidades ao mudar de mapa, a menos que especificado
            for group in [self.humans, self.enemies, self.projectiles, self.effects]:
                for entity in group: entity.kill()

        if map_name == "castle":
            # No castelo, current_stage é conceitualmente 0. O progresso da caçada está em last_hunt_stage.
             self.current_stage = 0
        elif "hunt" in map_name:
            # Ao iniciar uma caçada, usa o last_hunt_stage para definir o current_stage
            # start_new_stage irá então incrementá-lo
            self.current_stage = self.last_hunt_stage
            self.start_new_stage()


    def start_new_stage(self): # MODIFICADO PARA GERAR INIMIGOS VARIADOS
        self.current_stage += 1 # Incrementa para o novo estágio
        print(f"--- Stage {self.current_stage} ---")
        for h in self.humans: h.kill() # Limpa humanos do estágio anterior
        for e in self.enemies: e.kill() # Limpa inimigos do estágio anterior

        num_humans = BASE_HUMANS_PER_STAGE + (self.current_stage -1) * HUMANS_INCREMENT_PER_STAGE
        total_num_enemies = BASE_ENEMIES_PER_STAGE + (self.current_stage-1) * ENEMIES_INCREMENT_PER_STAGE
        
        current_speed_multiplier = 1.0 + (self.current_stage-1) * (ENEMY_SPEED_INCREMENT_PER_STAGE / ENEMY_BASE_SPEED)

        for _ in range(num_humans):
            h_pos = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
            human = Human(h_pos); self.humans.add(human); self.all_sprites.add(human)

        for _ in range(total_num_enemies):
            e_pos = (random.choice([random.randint(0,50), random.randint(WIDTH-50, WIDTH)]),
                     random.choice([random.randint(0,50), random.randint(HEIGHT-50, HEIGHT)]))
            EnemyClass = random.choice(ENEMY_TYPES)
            enemy_instance = EnemyClass(e_pos, speed_multiplier=current_speed_multiplier)
            enemy_sprite_size = enemy_instance.rect.size
            # Evitar spawn em cima do vampiro (ou muito perto)
            if self.vampire: # Checa se o vampiro existe
                v_rect_inflated = self.vampire.rect.inflate(100,100)
                while pygame.Rect(e_pos[0] - enemy_sprite_size[0]//2, e_pos[1] - enemy_sprite_size[1]//2, enemy_sprite_size[0], enemy_sprite_size[1]).colliderect(v_rect_inflated) :
                     e_pos = (random.choice([random.randint(0,50), random.randint(WIDTH-50, WIDTH)]),
                              random.choice([random.randint(0,50), random.randint(HEIGHT-50, HEIGHT)]))
                     enemy_instance.rect.center = e_pos # Atualiza a posição se foi movido
            
            self.enemies.add(enemy_instance)
            self.all_sprites.add(enemy_instance)

    def add_projectile(self, projectile_or_list):
        if projectile_or_list:
            items_to_add = projectile_or_list if isinstance(projectile_or_list, list) else [projectile_or_list]
            for p_item in items_to_add:
                if p_item: self.projectiles.add(p_item); self.all_sprites.add(p_item)

    def add_effect(self, effect_sprite):
        if effect_sprite: self.effects.add(effect_sprite); self.all_sprites.add(effect_sprite)

    def save_game(self): # <<< MODIFICADO / NOVO
        if not self.vampire: return False
        data_to_save = {
            'vampire': {
                'hp': self.vampire.hp,
                'max_hp': self.vampire.max_hp,
                'exp': self.vampire.exp,
                'level': self.vampire.level,
                'vampiric_strength': self.vampire.vampiric_strength,
                'equipped_spell_id': self.vampire.equipped_spell_id,
                'spells_unlocked': [spell_id for spell_id, data in self.vampire.spells.items() if data['unlocked']],
                'pos': list(self.vampire.rect.center) # Salva a posição no castelo
            },
            'game_state': {
                'current_map': self.current_map, # Deveria ser "castle" ao salvar
                'last_hunt_stage': self.last_hunt_stage, # Salva o progresso da caçada
            }
        }
        try:
            with open(SAVE_FILENAME, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print("Game Saved!")
            self.save_load_message_text = "Game Saved!"
            self.show_save_load_message_timer = pygame.time.get_ticks() + 2000 # Exibe por 2 segundos
            return True
        except IOError as e:
            print(f"Error saving game: {e}")
            self.save_load_message_text = "Error Saving Game!"
            self.show_save_load_message_timer = pygame.time.get_ticks() + 2000
            return False

    def load_game(self): # <<< MODIFICADO / NOVO
        try:
            with open(SAVE_FILENAME, 'r') as f:
                loaded_data = json.load(f)
            
            if not self.vampire: # Se o vampiro não existe, cria um novo
                self.vampire = Vampire((WIDTH // 2, HEIGHT // 2))
            else: # Se existe, atualiza seus atributos
                self.vampire.kill() # Remove o vampiro antigo dos grupos de sprites
                self.vampire = Vampire((WIDTH // 2, HEIGHT // 2)) # Cria uma nova instância limpa

            # Carrega dados do vampiro
            v_data = loaded_data['vampire']
            self.vampire.hp = v_data['hp']
            self.vampire.max_hp = v_data['max_hp']
            self.vampire.exp = v_data['exp']
            self.vampire.level = v_data['level']
            self.vampire.vampiric_strength = v_data['vampiric_strength']
            self.vampire.equipped_spell_id = v_data['equipped_spell_id']
            self.vampire.rect.center = tuple(v_data.get('pos', (WIDTH // 2, HEIGHT // 2)))

            self.vampire.spells = {} # Limpa magias existentes
            for spell_id in v_data.get('spells_unlocked', []):
                if spell_id in SPELLS_DATA:
                    self.vampire.spells[spell_id] = {
                        'unlocked': True,
                        'last_used': 0, # Reseta cooldowns ao carregar
                        'data': SPELLS_DATA[spell_id]
                    }
            
            gs_data = loaded_data['game_state']
            self.last_hunt_stage = gs_data.get('last_hunt_stage', 0)
            # Força o jogador a estar no castelo após carregar
            self.current_map = "castle" 
            self.current_stage = 0 # No castelo, o "stage" é 0. O progresso da caçada está em last_hunt_stage.

            self.setup_game(from_load=True) # Reconfigura o jogo com dados carregados

            print("Game Loaded!")
            self.save_load_message_text = "Game Loaded!"
            self.show_save_load_message_timer = pygame.time.get_ticks() + 2000
            return True
        except FileNotFoundError:
            print("No save file found.")
            self.save_load_message_text = "No Save File Found."
            self.show_save_load_message_timer = pygame.time.get_ticks() + 2000
            return False
        except (IOError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading game: {e}")
            self.save_load_message_text = "Error Loading Game! Resetting."
            self.show_save_load_message_timer = pygame.time.get_ticks() + 3000
            self.setup_game() # Reseta para o estado inicial se o save estiver corrompido
            return False


    def handle_input(self): # <<< MODIFICADO
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if self.game_over_flag:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.setup_game()
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.paused = not self.paused
                if self.paused and event.key != pygame.K_ESCAPE: continue
                
                if self.current_map == "castle":
                    if event.key == pygame.K_F5: self.save_game()
                    elif event.key == pygame.K_F9: self.load_game()

                if event.key == pygame.K_F1: self.change_map("castle")
                elif event.key == pygame.K_F2: self.change_map("hunt_forest")
                elif event.key == pygame.K_F3: self.change_map("hunt_village")
                
                if not self.paused: # Ações de jogo só se não estiver pausado
                    if event.key == pygame.K_SPACE:
                        if self.vampire: self.add_projectile(self.vampire.shoot())
                    if event.key == pygame.K_f:
                        if self.vampire:
                            spell_sprites = self.vampire.use_equipped_spell()
                            if spell_sprites:
                                for item in spell_sprites:
                                    if isinstance(item, Projectile): self.add_projectile(item)
                                    else: self.add_effect(item)
                    if self.current_map == "castle":
                        if self.vampire:
                            for spell_id, data in SPELLS_DATA.items():
                                if event.key == data['key_to_equip']: self.vampire.equip_spell(spell_id); break
                            if event.key == pygame.K_0: self.vampire.equip_spell(None)

        if not self.game_over_flag and not self.paused and self.vampire: # Adicionado self.vampire
            self.vampire.update(keys, self)
        return True

    def update_game_logic(self): # <<< MODIFICADO
        if self.game_over_flag or self.paused: return
        if not self.vampire: return # Adicionado para segurança

        if self.current_map != "castle":
            for enemy in list(self.enemies):
                enemy.update(self.vampire.rect.center)
                if self.vampire.rect.colliderect(enemy.rect):
                    if self.vampire.take_damage(enemy.damage_to_vampire):
                        self.game_over_flag = True; self.restart_timer = pygame.time.get_ticks() + 5000
                        print("Vampire Died!")
                        break
                    else:
                        push_vec = pygame.Vector2(enemy.rect.center) - pygame.Vector2(self.vampire.rect.center)
                        if push_vec.length_squared() > 0: enemy.rect.move_ip(push_vec.normalize() * 5)
                        else: enemy.rect.x += 10 # Fallback se estiverem exatamente no mesmo ponto
        self.projectiles.update()
        self.effects.update()

        if self.current_map != "castle":
            for human in pygame.sprite.spritecollide(self.vampire, self.humans, False):
                if not human.sucked:
                    human.get_sucked()
                    self.vampire.gain_exp(EXP_PER_HUMAN)
                    self.vampire.increase_vampiric_strength()
                    self.vampire.hp = min(self.vampire.max_hp, self.vampire.hp + 5)

        for proj in list(self.projectiles):
            if not isinstance(proj, BloodBombProjectile) and hasattr(proj, 'damage') and proj.damage > 0:
                hit_enemies_list = pygame.sprite.spritecollide(proj, self.enemies, False)
                for enemy_hit in hit_enemies_list:
                    if enemy_hit.take_damage(proj.damage):
                        self.vampire.gain_exp(enemy_hit.exp_value)
                    proj.kill()
                    break 
        
        for effect in list(self.effects):
            if isinstance(effect, BloodBombExplosion):
                exploded_enemies_list = pygame.sprite.spritecollide(effect, self.enemies, False)
                for enemy_hit in exploded_enemies_list:
                    if enemy_hit.take_damage(effect.damage):
                         self.vampire.gain_exp(enemy_hit.exp_value * 1.5)

        if self.current_map != "castle" and self.current_stage > 0:
            all_sucked = all(h.sucked for h in self.humans) if self.humans else True
            if all_sucked and not self.enemies:
                print("Stage Clear! Advancing.")
                self.start_new_stage()

    def draw_hud(self): # <<< MODIFICADO
        if not self.vampire: return # Adicionado para segurança

        hp_surf = FONT_SMALL.render(f"HP: {int(self.vampire.hp)}/{self.vampire.max_hp}", True, WHITE)
        lvl_surf = FONT_SMALL.render(f"Level: {self.vampire.level} ({self.vampire.exp}/{EXP_TO_LEVEL_UP_BASE*self.vampire.level})", True, WHITE)
        title_surf = FONT_SMALL.render(f"Title: {self.vampire.title}", True, WHITE)
        str_surf = FONT_SMALL.render(f"Strength: {self.vampire.vampiric_strength}", True, WHITE)
        screen.blit(hp_surf, (10,10)); screen.blit(lvl_surf, (10,30)); screen.blit(title_surf, (10,50)); screen.blit(str_surf, (10,70))

        map_surf = FONT_SMALL.render(f"Map: {self.current_map.replace('_',' ').title()}", True, WHITE)
        screen.blit(map_surf, (WIDTH - map_surf.get_width() - 10, 10))

        if self.current_map == "castle" and self.last_hunt_stage > 0:
            hunt_prog_surf = FONT_SMALL.render(f"Hunt Stage: {self.last_hunt_stage}", True, YELLOW)
            screen.blit(hunt_prog_surf, (WIDTH - hunt_prog_surf.get_width() - 10, 30))
        elif "hunt" in self.current_map:
            stage_surf = FONT_SMALL.render(f"Stage: {self.current_stage}", True, WHITE)
            screen.blit(stage_surf, (WIDTH - stage_surf.get_width() - 10, 30))
            h_left = sum(1 for h in self.humans if not h.sucked)
            h_surf = FONT_SMALL.render(f"Humans: {h_left}", True, WHITE if h_left > 0 else YELLOW)
            screen.blit(h_surf, (WIDTH - h_surf.get_width() - 10, 50))
            e_surf = FONT_SMALL.render(f"Enemies: {len(self.enemies)}", True, WHITE if self.enemies else YELLOW)
            screen.blit(e_surf, (WIDTH - e_surf.get_width() - 10, 70))

        if self.vampire.equipped_spell_id and self.vampire.equipped_spell_id in self.vampire.spells:
            s_info = self.vampire.spells[self.vampire.equipped_spell_id]
            s_name = s_info['data']['name']
            s_cd_total = s_info['data']['cooldown']
            s_cd_rem = max(0, s_cd_total - (pygame.time.get_ticks() - s_info['last_used']))
            s_status = f"Equipped: {s_name}" + (f" (CD: {s_cd_rem/1000:.1f}s)" if s_cd_rem > 0 else " (Ready!)")
            spell_surf = FONT_SMALL.render(s_status, True, WHITE)
            screen.blit(spell_surf, (10, HEIGHT - 30))

        if self.current_map == "castle":
            y_offset = HEIGHT - 120 # Ajustado para mais uma linha
            help_texts = [
                "Castle: Equip spells (0 to unequip).",
                "[F1] Castle | [F2] Forest | [F3] Village",
                "[F5] Save Game | [F9] Load Game" # <<< NOVA LINHA
            ]
            for text in help_texts:
                help_surf = FONT_SMALL.render(text, True, YELLOW)
                screen.blit(help_surf, (10, y_offset)); y_offset += 20
            
            for s_id, s_data_dict in self.vampire.spells.items():
                if s_data_dict['unlocked']:
                    key_char = pygame.key.name(SPELLS_DATA[s_id]['key_to_equip']).upper()
                    s_text = f"[{key_char}] {s_data_dict['data']['name']}" + (" (EQUIPPED)" if self.vampire.equipped_spell_id == s_id else "")
                    color = GREEN if self.vampire.equipped_spell_id == s_id else WHITE
                    list_surf = FONT_SMALL.render(s_text, True, color)
                    screen.blit(list_surf, (10, y_offset)); y_offset += 20
        
        if self.show_save_load_message_timer > pygame.time.get_ticks():
            msg_surf = FONT_MEDIUM.render(self.save_load_message_text, True, YELLOW)
            screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH // 2, HEIGHT - 50)))
        elif self.show_save_load_message_timer != 0:
            self.show_save_load_message_timer = 0
            self.save_load_message_text = ""
    
    def draw_elements(self):
        if "hunt" in self.current_map:
            if GRASS_TILE_IMG:
                tile_w, tile_h = GRASS_TILE_IMG.get_size()
                for x in range(0, WIDTH, tile_w):
                    for y in range(0, HEIGHT, tile_h): screen.blit(GRASS_TILE_IMG, (x,y))
            else: screen.fill(GREEN) # Cor de fundo para caça
        elif self.current_map == "castle": screen.fill(BLACK)
        else: screen.fill(GRAY) # Cor de fundo genérica
        
        self.all_sprites.draw(screen)
        self.draw_hud()

        if self.game_over_flag:
            overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            go_surf = FONT_LARGE.render("VOCÊ MORREU!", True, RED)
            screen.blit(go_surf, go_surf.get_rect(center=(WIDTH//2, HEIGHT//2-30)))
            msg = "Pressione 'R' para reiniciar"
            if self.restart_timer>0 and pygame.time.get_ticks()<self.restart_timer: msg = f"Reiniciando em {(self.restart_timer-pygame.time.get_ticks())//1000}s... ou 'R'"
            elif self.restart_timer>0 and pygame.time.get_ticks()>=self.restart_timer: self.setup_game(); return # Auto-restart
            rs_surf = FONT_MEDIUM.render(msg, True, WHITE)
            screen.blit(rs_surf, rs_surf.get_rect(center=(WIDTH//2, HEIGHT//2+20)))
        
        if self.paused:
            overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,150)); screen.blit(overlay,(0,0))
            p_surf = FONT_LARGE.render("PAUSADO", True, YELLOW)
            screen.blit(p_surf, p_surf.get_rect(center=(WIDTH//2, HEIGHT//2)))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            if not self.handle_input(): running = False; continue
            
            # Somente atualiza a lógica e desenha se não estivermos no meio de um auto-restart
            # Isso evita um flicker ou um frame de jogo antes do setup_game() completar no auto-restart
            if not (self.game_over_flag and self.restart_timer > 0 and pygame.time.get_ticks() >= self.restart_timer):
                self.update_game_logic()
                self.draw_elements()
            elif self.game_over_flag and self.restart_timer > 0 and pygame.time.get_ticks() >= self.restart_timer:
                # Garante que o setup_game é chamado se o auto-restart foi acionado
                # A condição de draw_elements e update_game_logic já lida com o não processamento
                # E a condição do game_over_flag em draw_elements lida com o auto-restart chamando setup_game
                pass


        pygame.quit()

# === PONTO DE ENTRADA ===
if __name__ == '__main__':
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    create_sprites_and_tiles() # Carrega assets
    game_state = GameState() # Inicializa o estado do jogo
    game_state.run() # Inicia o loop principal