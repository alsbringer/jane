import pygame
from os.path import join

# Blue Print
class Platforms:
    def __init__(self,left, top, right, bottom, height, width, img):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom
            self.height = height
            self.width = width
            self.img = img

class Jane:
    def __init__(self,left, top, img):
        self.left = left
        self.top = top
        self.height = img.get_height()
        self.width = img.get_width()
        self.right = self.left + self.width
        self.bottom = self.top + self.height
        self.img = img
        

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

def calc_align_right(image):
    return WINDOW_WIDTH - image.get_width()

def calc_align_bottom(image):
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
jane_img = loadImage(join("assets/jane1.png")).convert_alpha()
jane_img = setSize_W(jane_img, 100)

jane = Jane(left=0, top=WINDOW_HEIGHT - jane_img.get_height(), img=jane_img)

jane_direction = "right"
forward_blocked = False
toback_blocked = False
jumping = False
can_jump = True
can_double_jump = False
going_up = False
ground = WINDOW_HEIGHT
jump_height = 200
extra_jump_height = 0
on_platform = False

# --- Cheese Setup ---
cheese_img = loadImage("assets/cheese.png").convert_alpha()
cheese_img = setSize_W(cheese_img, 40)
cheese_x = calc_align_right(cheese_img) - cheese_img.get_width()
cheese_y = calc_align_bottom(cheese_img)
cheese_right = cheese_x+ cheese_img.get_width()
cheese_taken = False
cheese_facing_right = True

# --- Firewall Setup ---
firewall_img = loadImage("assets/firewall.png").convert_alpha()
firewall_img = setSize_WH(firewall_img, 100, 200)
firewall_left = calc_align_right(firewall_img) - 400
firewall_top = int(calc_align_bottom(firewall_img) + firewall_img.get_height() / 3)
firewall_w = firewall_img.get_width()
firewall_h = firewall_img.get_height()
firewall_right = firewall_left + firewall_w
firewall_bottom = firewall_top + firewall_h

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
                print("can_jump:", can_jump)
                if can_double_jump and not can_jump:
                    print("second jump at", jane.bottom)
                    going_up = True
                    extra_jump_height += 80
                    can_double_jump = False
                elif can_jump:
                    jumping = True
                    going_up = True
                    can_jump = False
                    can_double_jump = True
                    print("Jumping:", jumping, "at", jane.bottom)
                    starting_ground = ground
            if event.key == pygame.K_f:
                if (
                    jane.right >= cheese_x and jane.right <= cheese_right
                    or jane.left >= cheese_x and jane.left <= cheese_right 
                    ):
                    if cheese_taken: cheese_taken = False
                    else: cheese_taken = True

    # Input(move forward, move backward), logic(flip avatar)
    if keys[pygame.K_d]:
        if not forward_blocked:
            jane.left += Mov
            if jane_direction != "right":
                jane_direction = "right"
                jane.img = flip_x(jane.img)
        # else: print("forward Blocked"
    if keys[pygame.K_a] and not toback_blocked:
        jane.left -= Mov
        if jane_direction != "left":
            jane_direction = "left"
            jane.img = flip_x(jane.img)

    # update value
    jane.right = jane.left + jane.width
        

    # logic(collision blocking)
    if (
        (jane.right >= firewall_left + int(firewall_w / 2) - 20)   
        and 
        (jane.right <= firewall_left + int(firewall_w / 2) + 20)
        and 
        (jane.bottom > firewall_top + 34)
        ):
        forward_blocked = True
    else:
        forward_blocked = False    
    if (
        (jane.left >= firewall_left + int(firewall_w / 2) - 20 )
        and 
        (jane.left <= firewall_left + int(firewall_w / 2) + 20)
        and
        (jane.bottom > firewall_top + 34)
        ):
        toback_blocked = True
    else:
        toback_blocked = False

    # logic(ganti ground ke firewall)
    if (jane.bottom <= firewall_top + 34
        and jane.right >= firewall_left
        and jane.left <= firewall_right):
        on_platform = True
        ground = firewall_top + 34
    else:
        on_platform = False

    # logic(ganti ke window ground)
    if not on_platform:
        ground = WINDOW_HEIGHT
    
    if ground != prev_ground:
        print("ground berubah")
        print("on platform", on_platform)
        if not on_platform and not jumping:
            print("guing_up false")
            jumping = True
            going_up = False
    
    # log(ground changing)
    if ground != prev_ground:
        print("prev ground: ", prev_ground)
        print("current ground ", ground)
    
    # logic(jump), log(foot coordinate)
    if jumping:
        # start jumping
        if going_up:
            jane.bottom -= 10
            jane.top = jane.bottom - jane.height
            print("going up: ", jane.bottom)
        # reach maxiimun
        elif not going_up and jane.bottom < ground:
            print("going down: ", jane.bottom)
            jane.bottom += 10
            jane.top = jane.bottom - jane.height
        # reach the ground === makes stay
        if jane.bottom >= ground:
            jumping = False
            can_jump = True
            print("on the ground: ", jane.bottom)
            can_double_jump = False
            extra_jump_height = 0
        #fall switch === makes fall permission
        if starting_ground - jane.bottom >= (jump_height + extra_jump_height) and going_up:
            print("fall at", jane.bottom)
            print("jump height:", jump_height+ extra_jump_height)
            going_up = False
            
    # --- Render ---
    display.fill("black")
    
    if jane.left <= (firewall_right/ 2):
        
        sprites = [
            (firewall_img, firewall_left, firewall_top),
            (jane.img, jane.left, jane.top),
        ]
        
    else:
        sprites = [
            (jane.img, jane.left, jane.top),
            (firewall_img, firewall_left, firewall_top),
        ]

    for sprite, sx, sy in sprites:
        display.blit(sprite, (sx, sy))
    
    # cheese render
    if cheese_taken:
        if jane_direction =="right":
            cheese_x = jane.right - 40
            cheese_y = jane.bottom - 40
            display.blit(cheese_img, (cheese_x, cheese_y))
        if jane_direction == "left":
            cheese_x = jane.left
            cheese_y = jane.bottom - 40
            display.blit(cheese_img, (cheese_x, cheese_y))
    else:
        cheese_y = calc_align_bottom(cheese_img)
        display.blit(cheese_img, (cheese_x, cheese_y))
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()