import pygame
from os.path import join

# --- Utility Functions ---
def setSize_W(image, width): 
    w, h = image.get_size()
    ratio = w / h
    height = int(width / ratio)
    return pygame.transform.scale(image, (width, height))

def setSize_WH(image, width, height):
    return pygame.transform.scale(image, (width, height))

def loadImage(path):
    return pygame.image.load(path)

def right_edge(image):
    return WINDOW_WIDTH - image.get_width()

def bottom_edge(image):
    return WINDOW_HEIGHT - image.get_height()

def flip_x(image):
    return pygame.transform.flip(image, True, False)

def flip_y(image):
    return pygame.transform.flip(image, False, True)

def flip_xy(image):
    return pygame.transform.flip(image, True, True)

def fade_on_approach(jane_x, target_x, target_img):
    distance = target_x - jane_x
    if distance <= 100:
        target_img.set_alpha(int(255 * distance / 100))
    else:
        target_img.set_alpha(255)


# --- Window Setup ---
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 500
pygame.init()
display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

# --- Jane Setup ---
jane_img = loadImage(join("assets\jane1.png")).convert_alpha()
jane_img = setSize_W(jane_img, 100)

jane_width = jane_img.get_width()
jane_height = jane_img.get_height()

jane_x1 = 0
jane_y1 = WINDOW_HEIGHT - jane_img.get_height()
jane_x2 = jane_x1 + jane_width
jane_y2 = jane_y1 + jane_height

jane_facing_right = True
forward_blocked = False
toback_blocked = False
jumping = False
can_jump = True
can_double_jump = False
going_up = False
ground = WINDOW_HEIGHT
jump_height = 80
extra_jump_height = 0
on_platform = False
on_ground = True
is_falling = False

# --- Cheese Setup ---
cheese_img = loadImage("assets/cheese.png").convert_alpha()
cheese_img = setSize_W(cheese_img, 40)
cheese_x = right_edge(cheese_img) - cheese_img.get_width()
cheese_y = bottom_edge(cheese_img)
cheese_right = cheese_x+ cheese_img.get_width()
cheese_taken = False
cheese_facing_right = True

# --- Firewall Setup ---
firewall_img = loadImage("assets/firewall.png").convert_alpha()
firewall_img = setSize_WH(firewall_img, 100, 200)
firewall_x = right_edge(firewall_img) - 400
firewall_y = int(bottom_edge(firewall_img) + firewall_img.get_height() / 3)
firewall_w = firewall_img.get_width()
firewall_h = firewall_img.get_height()
firewall_right = firewall_x + firewall_w
firewall_bottom = firewall_y + firewall_h

# --- Movement ---
Mov = 10
starting_ground = WINDOW_HEIGHT

# --- Main Loop ---
running = True
while running:
    prev_ground = ground
    keys = pygame.key.get_pressed()
    
    # input(double jump, take cheese), log(jump coordinate, double jump coordinate)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if can_double_jump and not can_jump:
                    print("second jump at", jane_y2)
                    going_up = True
                    extra_jump_height += 80
                    can_double_jump = False
                elif can_jump:
                    jumping = True
                    going_up = True
                    can_jump = False
                    can_double_jump = True
                    print("Jumping:", jumping, "at", jane_y2)
                    starting_ground = ground
            if event.key == pygame.K_f:
                if (
                    jane_x2 >= cheese_x and jane_x2 <= cheese_right
                    or jane_x1 >= cheese_x and jane_x1 <= cheese_right 
                    ):
                    if cheese_taken: cheese_taken = False
                    else: cheese_taken = True

    # Input(move forward, move backward), logic(flip avatar)
    if keys[pygame.K_d]:
        if not forward_blocked:
            jane_x1 += Mov
            if not jane_facing_right:
                jane_facing_right = True
                jane_img = flip_x(jane_img)
        # else: print("forward Blocked"
    if keys[pygame.K_a] and not toback_blocked:
        jane_x1 -= Mov
        if jane_facing_right:
            jane_facing_right = False
            jane_img = flip_x(jane_img)

    # update value
    jane_x2 = jane_x1 + jane_width
    jane_y1 = jane_y2 - jane_height
        

    # logic(collision blocking)
    if (
        (jane_x2 >= firewall_x + int(firewall_w / 2) - 20)
        and 
        (jane_x2 <= firewall_x + int(firewall_w / 2) + 20)
        and 
        (jane_y2 > firewall_y + 34)
        ):
        forward_blocked = True
    else:
        forward_blocked = False    
    if (
        (jane_x1 >= firewall_x + int(firewall_w / 2) - 20 )
        and 
        (jane_x1 <= firewall_x + int(firewall_w / 2) + 20)
        and
        (jane_y2 > firewall_y + 34)
        ):
        toback_blocked = True
    else:
        toback_blocked = False

    # logic(stand on firewall)
    if (jane_y2 <= firewall_y + 34
        and jane_x2 >= firewall_x
        and jane_x1 <= firewall_right):
        on_platform = True
        ground = firewall_y + 34
    else:
        on_platform = False

    # logic(fall from firewall)
    if not on_platform:
        ground = WINDOW_HEIGHT
    if ground != prev_ground:
        jumping = True
        going_up = False
    
    # log(ground changing)
    if ground != prev_ground:
        print("prev ground: ", prev_ground)
        print("current ground ", ground)
    
    # logic(jump), log(foot coordinate)
    if jumping:
        # start jumping
        if going_up and jump_height >= 10:
            jane_y2 -= 10
            print("going up: ", jane_y2)
        # reach maxiimun
        elif not going_up and jane_y2 < ground:
            print("going down: ", jane_y2)
            jane_y2 += 10
        # reach the ground
        if jane_y2 >= ground:
            jumping = False
            can_jump = True
            print("on the ground: ", jane_y2)
            can_double_jump = False
            extra_jump_height = 0
        #fall switch
        if starting_ground - jane_y2 >= (jump_height + extra_jump_height) and going_up:
            print("fall at", jane_y2)
            print("jump height:", jump_height+ extra_jump_height)
            going_up = False
            
    # --- Render ---
    display.fill("black")
    
    if jane_x1 <= (firewall_x + firewall_w / 2):
        
        sprites = [
            (firewall_img, firewall_x, firewall_y),
            (jane_img, jane_x1, jane_y2 - jane_height),
        ]
        
    else:
        sprites = [
            (jane_img, jane_x1, jane_y2 - jane_height),
            (firewall_img, firewall_x, firewall_y),
        ]

    for sprite, sx, sy in sprites:
        display.blit(sprite, (sx, sy))
    
    # cheese render
    if cheese_taken:
        if jane_facing_right:
            cheese_x = jane_x2 - 40
            cheese_y = jane_y2 - 40
            display.blit(cheese_img, (cheese_x, cheese_y))
        if not jane_facing_right:
            cheese_x = jane_x1
            cheese_y = jane_y2 - 40
            display.blit(cheese_img, (cheese_x, cheese_y))
    else:
        cheese_y = bottom_edge(cheese_img)
        display.blit(cheese_img, (cheese_x, cheese_y))
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()