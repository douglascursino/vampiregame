import pygame
import random
import math
import os # Importar o módulo os

pygame.init()
pygame.font.init()

# === CONSTANTES ===
WIDTH, HEIGHT = 800, 600
FPS = 60

# Cores (ainda podem ser úteis para HUD, fundo, ou fallbacks)
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

# --- Caminho para a pasta de sprites ---
SPRITE_PATH = os.path.join("assets", "sprites")

# --- Tamanhos dos sprites (para redimensionamento) ---
VAMPIRE_SIZE = (50, 50)
HUMAN_SIZE = (40, 40)
ENEMY_SIZE = (100, 100)
PROJECTILE_SIZE_NORMAL = (15, 15)
PROJECTILE_SIZE_BLOODBOMB = (25, 25)
PROJECTILE_SIZE_NIGHTBEAM = (75, 15) # Largura x Altura

# === ASSETS GLOBAIS (SPRITES PRÉ-RENDERIZADOS) ===
SPRITES = {}

def load_sprite_image(filename, size, use_alpha=True):
    """Função auxiliar para carregar e redimensionar sprites."""
    path = os.path.join(SPRITE_PATH, filename)
    try:
        image = pygame.image.load(path)
        if use_alpha:
            image = image.convert_alpha() # Para PNGs com transparência
        else:
            image = image.convert() # Para JPEGs ou imagens sem alfa
        image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Erro ao carregar imagem '{path}': {e}. Usando sprite padrão.")
        # Cria um sprite placeholder simples se o carregamento falhar
        fallback_surface = pygame.Surface(size, pygame.SRCALPHA)
        fallback_surface.fill((255, 0, 255, 100)) # Magenta semi-transparente
        pygame.draw.rect(fallback_surface, WHITE, fallback_surface.get_rect(), 1)
        return fallback_surface

def create_sprites():
    # Vampiro
    SPRITES['vampire'] = load_sprite_image("vampire.png", VAMPIRE_SIZE)
    if SPRITES['vampire'].get_at((0,0)) == (255,0,255,100): # Checa se é o fallback
        v_surface = pygame.Surface(VAMPIRE_SIZE, pygame.SRCALPHA)
        pygame.draw.ellipse(v_surface, SKIN, (10, 0, 20, 20))
        pygame.draw.rect(v_surface, DARK_RED, (5, 20, 30, 20))
        pygame.draw.polygon(v_surface, BLACK, [(5, 20), (35, 20), (20, 35)])
        SPRITES['vampire'] = v_surface


    # Humano Vivo
    SPRITES['human_alive'] = load_sprite_image("human_alive.png", HUMAN_SIZE)
    if SPRITES['human_alive'].get_at((0,0)) == (255,0,255,100):
        h_surface = pygame.Surface(HUMAN_SIZE, pygame.SRCALPHA)
        pygame.draw.circle(h_surface, SKIN, (10, 6), 6)
        pygame.draw.rect(h_surface, BLUE, (4, 12, 12, 8))
        SPRITES['human_alive'] = h_surface

    # Humano Morto/Sugado
    SPRITES['human_dead'] = load_sprite_image("human_dead.png", HUMAN_SIZE)
    if SPRITES['human_dead'].get_at((0,0)) == (255,0,255,100):
        hd_surface = pygame.Surface(HUMAN_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(hd_surface, GRAY, (2, 8, 16, 6))
        pygame.draw.circle(hd_surface, SKIN, (7, 7), 4)
        SPRITES['human_dead'] = hd_surface

    # Inimigo
    SPRITES['enemy'] = load_sprite_image("enemy.png", ENEMY_SIZE)
    if SPRITES['enemy'].get_at((0,0)) == (255,0,255,100):
        e_surface = pygame.Surface(ENEMY_SIZE, pygame.SRCALPHA)
        pygame.draw.ellipse(e_surface, PURPLE, (0, 0, 30, 30))
        pygame.draw.circle(e_surface, RED, (10, 10), 4)
        pygame.draw.circle(e_surface, RED, (20, 10), 4)
        SPRITES['enemy'] = e_surface

    # Projétil Normal
    SPRITES['projectile'] = load_sprite_image("projectile.png", PROJECTILE_SIZE_NORMAL)
    if SPRITES['projectile'].get_at((0,0)) == (255,0,255,100):
        p_surface = pygame.Surface(PROJECTILE_SIZE_NORMAL)
        p_surface.fill(RED)
        SPRITES['projectile'] = p_surface

    # Bomba de Sangue (projétil)
    SPRITES['blood_bomb_projectile'] = load_sprite_image("blood_bomb_projectile.png", PROJECTILE_SIZE_BLOODBOMB)
    if SPRITES['blood_bomb_projectile'].get_at((0,0)) == (255,0,255,100):
        bb_surface = pygame.Surface(PROJECTILE_SIZE_BLOODBOMB, pygame.SRCALPHA)
        pygame.draw.circle(bb_surface, DARK_RED, (int(PROJECTILE_SIZE_BLOODBOMB[0]/2), int(PROJECTILE_SIZE_BLOODBOMB[1]/2)), int(PROJECTILE_SIZE_BLOODBOMB[0]/2))
        SPRITES['blood_bomb_projectile'] = bb_surface

    # Raio Noturno (projétil)
    SPRITES['night_beam_projectile'] = load_sprite_image("night_beam_projectile.png", PROJECTILE_SIZE_NIGHTBEAM)
    if SPRITES['night_beam_projectile'].get_at((0,0)) == (255,0,255,100):
        nb_surface = pygame.Surface(PROJECTILE_SIZE_NIGHTBEAM, pygame.SRCALPHA)
        nb_surface.fill(PURPLE)
        SPRITES['night_beam_projectile'] = nb_surface

# === CLASSES ===
# (Nenhuma alteração necessária nas definições das classes GameObject, Vampire, Human, Enemy, Projectile,
# BloodBombExplosion, BloodBombProjectile, pois elas já usam SPRITES[image_key])

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
        # print(f"Vampiric Strength: {self.vampiric_strength}, Shoot Cooldown: {self.shoot_cooldown}") # Removido para não poluir console

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
            # print(f"Used spell: {spell['data']['name']}") # Removido para não poluir console
            cast_direction = self.last_moved_direction
            if cast_direction.length_squared() == 0:
                cast_direction = pygame.Vector2(1,0)
            return spell['data']['activate_func'](self, cast_direction)
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
            self.image = SPRITES['human_dead'] # Troca para o sprite de humano morto

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
        self.damage = damage
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        if not screen.get_rect().contains(self.rect) or \
           pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

class BloodBombExplosion(GameObject): # A explosão ainda é desenhada, mas poderia ser uma imagem também
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        # Poderíamos carregar uma imagem para a explosão aqui também:
        # self.image = load_sprite_image("explosion.png", (80, 80))
        # Ou manter o desenho dinâmico:
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

class BloodBombProjectile(Projectile):
    def __init__(self, pos, direction_vector):
        super().__init__(pos, direction_vector, 'blood_bomb_projectile', speed=7, damage=0, lifetime=1000)
        self.exploded = False

    def update(self):
        super().update()
        if not self.alive() and not self.exploded:
            self.exploded = True
            if 'game_state' in globals():
                game_state.add_effect(BloodBombExplosion(self.rect.center))

# === FUNÇÕES DE MAGIA ===
def activate_blood_bomb(caster, caster_direction):
    return [BloodBombProjectile(caster.rect.center, caster_direction)]

def activate_night_beam(caster, caster_direction):
    return [Projectile(caster.rect.center, caster_direction, 'night_beam_projectile', speed=20, damage=25, lifetime=500)]

def activate_shadow_barrier(caster, caster_direction): # Não implementado
    return []

SPELLS_DATA = {
    'blood_bomb': {
        'name': "Blood Bomb", 'unlock_level': 3, 'cooldown': 8000,
        'activate_func': activate_blood_bomb, 'key_to_equip': pygame.K_1
    },
    'night_beam': {
        'name': "Night Beam", 'unlock_level': 6, 'cooldown': 5000,
        'activate_func': activate_night_beam, 'key_to_equip': pygame.K_2
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
        self.all_sprites.empty(); self.humans.empty(); self.enemies.empty()
        self.projectiles.empty(); self.effects.empty()
        self.all_sprites.add(self.vampire)
        self.current_stage = 0
        self.game_over_flag = False
        self.paused = False
        self.restart_timer = 0
        self.vampire.hp = self.vampire.max_hp
        self.vampire.exp = 0
        self.vampire.level = 1
        self.vampire.vampiric_strength = 0
        self.vampire.shoot_cooldown = BASE_SHOOT_COOLDOWN
        self.vampire.equipped_spell_id = None
        self.vampire.spells = {}
        self.vampire.check_spell_unlocks()
        self.vampire.update_title()
        self.change_map("castle")

    def change_map(self, map_name):
        self.current_map = map_name
        for group in [self.humans, self.enemies, self.projectiles, self.effects]:
            for entity in group: entity.kill()
        if map_name == "castle":
            pass # print("Entered the Castle.")
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
            human = Human(h_pos); self.humans.add(human); self.all_sprites.add(human)
        for _ in range(num_enemies):
            e_pos = (random.choice([random.randint(0,50), random.randint(WIDTH-50, WIDTH)]),
                     random.choice([random.randint(0,50), random.randint(HEIGHT-50, HEIGHT)]))
            enemy = Enemy(e_pos, enemy_current_speed)
            while self.vampire and pygame.Rect(e_pos, ENEMY_SIZE).colliderect(self.vampire.rect.inflate(100,100)) :
                 e_pos = (random.choice([random.randint(0,50), random.randint(WIDTH-50, WIDTH)]),
                          random.choice([random.randint(0,50), random.randint(HEIGHT-50, HEIGHT)]))
            enemy.rect.topleft = e_pos
            self.enemies.add(enemy); self.all_sprites.add(enemy)

    def add_projectile(self, projectile_or_list):
        if projectile_or_list:
            items_to_add = projectile_or_list if isinstance(projectile_or_list, list) else [projectile_or_list]
            for p_item in items_to_add:
                if p_item:
                    self.projectiles.add(p_item); self.all_sprites.add(p_item)

    def add_effect(self, effect_sprite):
        if effect_sprite:
            self.effects.add(effect_sprite); self.all_sprites.add(effect_sprite)

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

                if event.key == pygame.K_F1: self.change_map("castle")
                elif event.key == pygame.K_F2: self.change_map("hunt_forest")
                elif event.key == pygame.K_F3: self.change_map("hunt_village")
                if event.key == pygame.K_SPACE: self.add_projectile(self.vampire.shoot())
                if event.key == pygame.K_f:
                    spell_sprites = self.vampire.use_equipped_spell()
                    if spell_sprites:
                        for item in spell_sprites:
                            if isinstance(item, Projectile): self.add_projectile(item)
                            else: self.add_effect(item)
                if self.current_map == "castle":
                    for spell_id, data in SPELLS_DATA.items():
                        if event.key == data['key_to_equip']: self.vampire.equip_spell(spell_id); break
                    if event.key == pygame.K_0: self.vampire.equip_spell(None)
        if not self.game_over_flag and not self.paused:
            self.vampire.update(keys, self)
        return True

    def update_game_logic(self):
        if self.game_over_flag or self.paused: return

        if self.current_map != "castle":
            for enemy in self.enemies:
                enemy.update(self.vampire.rect.center)
                if self.vampire.rect.colliderect(enemy.rect):
                    if self.vampire.take_damage(15):
                        self.game_over_flag = True; self.restart_timer = pygame.time.get_ticks() + 5000
                        print("Vampire Died!")
                    else:
                        push_vec = pygame.Vector2(enemy.rect.center) - pygame.Vector2(self.vampire.rect.center)
                        if push_vec.length_squared() > 0: enemy.rect.move_ip(push_vec.normalize() * 5)
                        else: enemy.rect.x += 10
        self.projectiles.update()
        self.effects.update()

        if self.current_map != "castle":
            for human in pygame.sprite.spritecollide(self.vampire, self.humans, False):
                if not human.sucked:
                    human.get_sucked()
                    self.vampire.gain_exp(EXP_PER_HUMAN)
                    self.vampire.increase_vampiric_strength()
                    self.vampire.hp = min(self.vampire.max_hp, self.vampire.hp + 5)

        for proj in self.projectiles:
            if not isinstance(proj, BloodBombProjectile) and hasattr(proj, 'damage') and proj.damage > 0:
                for _ in pygame.sprite.spritecollide(proj, self.enemies, True):
                    self.vampire.gain_exp(EXP_PER_ENEMY); proj.kill()
        for effect in self.effects:
            if isinstance(effect, BloodBombExplosion):
                for _ in pygame.sprite.spritecollide(effect, self.enemies, True):
                    self.vampire.gain_exp(EXP_PER_ENEMY * 2)

        if self.current_map != "castle" and self.current_stage > 0:
            all_sucked = all(h.sucked for h in self.humans) if self.humans else True
            if all_sucked and not self.enemies:
                print("Stage Clear! Advancing.")
                self.start_new_stage()

    def draw_hud(self):
        hp_surf = FONT_SMALL.render(f"HP: {int(self.vampire.hp)}/{self.vampire.max_hp}", True, WHITE)
        lvl_surf = FONT_SMALL.render(f"Level: {self.vampire.level} ({self.vampire.exp}/{EXP_TO_LEVEL_UP_BASE*self.vampire.level})", True, WHITE)
        title_surf = FONT_SMALL.render(f"Title: {self.vampire.title}", True, WHITE)
        str_surf = FONT_SMALL.render(f"Strength: {self.vampire.vampiric_strength}", True, WHITE)
        screen.blit(hp_surf, (10,10)); screen.blit(lvl_surf, (10,30)); screen.blit(title_surf, (10,50)); screen.blit(str_surf, (10,70))

        map_surf = FONT_SMALL.render(f"Map: {self.current_map.replace('_',' ').title()}", True, WHITE)
        screen.blit(map_surf, (WIDTH - map_surf.get_width() - 10, 10))
        if "hunt" in self.current_map:
            stage_surf = FONT_SMALL.render(f"Stage: {self.current_stage}", True, WHITE)
            screen.blit(stage_surf, (WIDTH - stage_surf.get_width() - 10, 30))
            h_left = sum(1 for h in self.humans if not h.sucked)
            h_surf = FONT_SMALL.render(f"Humans: {h_left}", True, WHITE if h_left > 0 else YELLOW)
            screen.blit(h_surf, (WIDTH - h_surf.get_width() - 10, 50))
            e_surf = FONT_SMALL.render(f"Enemies: {len(self.enemies)}", True, WHITE if self.enemies else YELLOW)
            screen.blit(e_surf, (WIDTH - e_surf.get_width() - 10, 70))

        if self.vampire.equipped_spell_id:
            s_info = self.vampire.spells[self.vampire.equipped_spell_id]
            s_name = s_info['data']['name']
            s_cd_total = s_info['data']['cooldown']
            s_cd_rem = max(0, s_cd_total - (pygame.time.get_ticks() - s_info['last_used']))
            s_status = f"Equipped: {s_name}" + (f" (CD: {s_cd_rem/1000:.1f}s)" if s_cd_rem > 0 else " (Ready!)")
            spell_surf = FONT_SMALL.render(s_status, True, WHITE)
            screen.blit(spell_surf, (10, HEIGHT - 30))

        if self.current_map == "castle":
            y_offset = HEIGHT - 100
            help_surf = FONT_SMALL.render("Castle: Equip spells (0 to unequip).", True, YELLOW)
            screen.blit(help_surf, (10, y_offset)); y_offset += 20
            for s_id, s_data_dict in self.vampire.spells.items():
                if s_data_dict['unlocked']:
                    key_name = pygame.key.name(SPELLS_DATA[s_id]['key_to_equip']).upper()
                    s_text = f"[{key_name}] {s_data_dict['data']['name']}" + (" (EQUIPPED)" if self.vampire.equipped_spell_id == s_id else "")
                    color = GREEN if self.vampire.equipped_spell_id == s_id else WHITE
                    list_surf = FONT_SMALL.render(s_text, True, color)
                    screen.blit(list_surf, (10, y_offset)); y_offset += 20

    def draw_elements(self):
        bg_color = GREEN if "hunt" in self.current_map else BLACK if self.current_map == "castle" else GRAY
        screen.fill(bg_color)
        self.all_sprites.draw(screen)
        self.draw_hud()

        if self.game_over_flag:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay, (0,0))
            go_surf = FONT_LARGE.render("VOCÊ MORREU!", True, RED)
            screen.blit(go_surf, go_surf.get_rect(center=(WIDTH//2, HEIGHT//2-30)))
            msg = "Pressione 'R' para reiniciar"
            if self.restart_timer > 0 and pygame.time.get_ticks() < self.restart_timer:
                msg = f"Reiniciando em {(self.restart_timer - pygame.time.get_ticks())//1000}s... ou 'R'"
            elif self.restart_timer > 0 and pygame.time.get_ticks() >= self.restart_timer:
                self.setup_game(); return
            rs_surf = FONT_MEDIUM.render(msg, True, WHITE)
            screen.blit(rs_surf, rs_surf.get_rect(center=(WIDTH//2, HEIGHT//2+20)))
        if self.paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,150)); screen.blit(overlay, (0,0))
            p_surf = FONT_LARGE.render("PAUSADO", True, YELLOW)
            screen.blit(p_surf, p_surf.get_rect(center=(WIDTH//2, HEIGHT//2)))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            if not self.handle_input(): running = False; continue
            self.update_game_logic()
            self.draw_elements()
        pygame.quit()

# === PONTO DE ENTRADA ===
if __name__ == '__main__':
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    create_sprites() # Carrega os sprites (imagens ou fallbacks)
    game_state = GameState()
    game_state.run()