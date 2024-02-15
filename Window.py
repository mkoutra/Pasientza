# The window of the pasientza game using tkinter.
import os
import random
import copy
import tkinter as tk
from PIL import Image, ImageTk

from Cards import Card, Deck, SuitDeck

class GameWindow:
    def __init__(self, deck):
        # Create decks needed to play the game
        self.__deck = deck
        print("Initial Deck\n", self.__deck)
        self.__soros = Deck(full = False)   # Cards removed from deck
        self.__suit_decks:list = [SuitDeck() for _ in range(8)]
        self.__suit_decks_sizes:list = [-1 for _ in range(8)] # Number of cards in suitDecks

        # Window configuration
        self._win_dimensions = (1024, 800)
        # self._background = "darkgreen"
        self._background = "seagreen4"
        self._title = "Pasientza"

        self._card_img_folder = os.path.join("imgs", "card_imgs")
        self._card_dimensions = (100, 130)  # Card configuration
        self._card_images:dict = {}         # Card id, i.e. "10s" to card image

        self._all_SuitDeck_canvas:list = [] # SuitDeck canvas

        # Create root window
        self._root = tk.Tk()
        self._root.title(self._title)
        self._root.configure(background = self._background)
        self._root.geometry(str(self._win_dimensions[0])
                            + "x" + str(self._win_dimensions[1]))

        # Create Frames
        self._suitDecks_frame = tk.Frame(master = self._root, bg = self._background)
        self._deck_frame = tk.Frame(master = self._root, bg = self._background)
        self._soros_cards_frame = tk.Frame(master = self._root, bg = self._background)

        # Place frames on the root window
        self._suitDecks_frame.place(relx = 0, rely = 0.02, anchor = tk.NW)
        self._deck_frame.place(relx = 0, rely = .75, anchor = tk.NW)
        self._soros_cards_frame.place(relx = .2, rely = .75, anchor = tk.NW)

        self._load_cards(dim = self._card_dimensions) # Load Playing Cards

        # Create the 8 SuitDecks with Blank Images and place them on frame.
        for i in range(8):
            canv = tk.Canvas(master = self._suitDecks_frame,
                             width = self._card_dimensions[0],
                             height = self._card_dimensions[1])
            canv.grid(row = 0, column = i, padx = 10, sticky=tk.NW)
            canv.create_image(0, 0, anchor = tk.NW, 
                              image = self._card_images["Blank"])
            
            self._all_SuitDeck_canvas.append(canv)
        
        # Draw deck
        # self.deck_canvas = tk.Canvas(master = self._deck_frame,
                                # width = self._card_dimensions[0],
                                # height = self._card_dimensions[1])
        # self.deck_canvas.pack(padx = 10)
        # self.deck_canvas.create_image(0, 0, anchor = tk.NW,
                                #  image = self._card_images["Blue"])

        self._deck_button = tk.Button(master = self._deck_frame,
                                      image = self._card_images["Blue"],
                                      relief = tk.RAISED,
                                      command = self._deck_button_callback)
        self._deck_button.pack(padx = 10)
        # self._deck_button.place(relx = 0.05, rely = 0, anchor = tk.NW)

        # Create three cards Canvas
        self._soros_cards_canvas = tk.Canvas(master = self._soros_cards_frame,
                                width = self._card_dimensions[0],
                                height = self._card_dimensions[1])
        self._soros_cards_canvas.pack()

        # Create Buttons

        for i in range(8):
            but = tk.Button(master = self._root,
                            text = "Deck " + str(i + 1),
                            width = 6, height = 1,
                            command = lambda x = i : self._pick_suitDeck_callback(x))
            but.place(relx = 0.1 * i, rely = 0.02, anchor = tk.NW)


    def _draw_first_cards(self, deck:Deck, n:int = 3, inv:bool = False):
        """Given a deck, it draws the first n cards.
        n: int, default value is 3.
        inv: bool, if true prints the top n cards in reverse order
        (useful for soros) """
        x_overlap = 20
        y_overlap = 0

        # First n cards. (top_cards[0] is the deck's top card)
        top_cards = deck.first_cards(n)
        
        if (inv == True): top_cards.reverse()

        for i, card in enumerate(top_cards):
            card_img = self._card_images[card.id()]
            overlap_images(self._soros_cards_canvas, card_img,
                           x_overlap, y_overlap, i)

    def _deck_button_callback(self):
        print("Deck Button Pressed")
        if (self.__deck.isEmpty() == True):
            self.__soros.inverse()
            self.__deck = copy.deepcopy(self.__soros)
            self.__soros.empty()
            self.deck_canvas.create_image(0, 0, anchor = tk.NW,
                                     image = self._card_images["Blue"])
            self._deck_button.configure(image = self._card_images["Blue"])
            
        # Place cards in soros
        for _ in range(3): 
            card = self.__deck.pop()

            if (not isinstance(card, Card)):
                print("End of deck")
                self.deck_canvas.create_image(0, 0, anchor = tk.NW,
                                              image = self._card_images["Blank"])
                self._deck_button.configure(image = self._card_images["Blank"])
                break # for loop
            else:
                self.__soros.push(card.rank(), card.suit())
        print("Soros = \n", self.__soros)
        # Draw soros top three with the third card on top 
        self._draw_first_cards(deck = self.__soros, inv = True)
                

    def _pick_suitDeck_callback(self, deck_id:int):
        print(f"Button {deck_id} pressed")
        moving_card = self.__soros.pop()
        
        if (isinstance(moving_card, Card) == False): return
        try:
            self.__suit_decks[deck_id].push(moving_card.rank(), moving_card.suit())
        except:
            self.__soros.push(moving_card.rank(), moving_card.suit())
            print("ERROR: Unable to handle this move")
            return
        
        self.draw_suitDeck_card(deck_id = deck_id, card = moving_card,
                                i = self.__suit_decks[deck_id].nCards() - 1)
        
        self._draw_first_cards(deck = self.__soros, inv = True)

    # TODO add a method to draw soros

    def _load_cards(self, dim):
        """ Load the cards and resize them with the given dimensions dim"""
        # Load Deck
        for fname in os.listdir(self._card_img_folder):
            img = Image.open(os.path.join(self._card_img_folder ,fname))
            img = img.resize(dim)

            card_name = fname.strip(".png")
            self._card_images[card_name] = ImageTk.PhotoImage(img)
        
        # Load the Blank card
        img = Image.open(os.path.join("imgs" ,"Blank_img.jpg"))
        img = img.resize(dim)
        self._card_images["Blank"] = ImageTk.PhotoImage(img)

        # Load the Blue playing card
        img = Image.open(os.path.join("imgs" ,"Blue_playing_card.jpg"))
        img = img.resize(dim)
        self._card_images["Blue"] = ImageTk.PhotoImage(img)

    def draw_suitDeck_card(self, deck_id:int, card:Card, i:int):
        card_img = self._card_images[card.id()]        
        overlap_images(self._all_SuitDeck_canvas[deck_id], card_img, 0, 35, i)

    def draw(self):
        """Draw window"""
        self._root.mainloop()


# Helper functions
def find_card(cardname:str):
    """
    Finds the card with the cardname given and returns
    the image object for Tkinter frame, otherwise returns None.
    """
    try:
        img = Image.open(cardname)
        img = img.resize((100, 130))
    except:
        print("Error")
        return None

    return ImageTk.PhotoImage(img)

def overlap_images(canvas, img, overlap_x, overlap_y, n:int):
    """Insert the n-th image (counting starts from 0) on a canvas.
    Images overlap by overlap_x on x axis and by overlap_y on y axis.
    All images are assumed to have the same size."""

    # Modify canvas' size
    canvas.config(width = img.width() + n * overlap_x,
                  height = img.height() + n * overlap_y)

    # Draw image starting at position (n * overlap_x, n * overlap_y)
    # Anchor point is the axis origin
    canvas.create_image(n * overlap_x, n * overlap_y, anchor = tk.NW, image = img)

if __name__ == "__main__":
    random.seed(100)
    d = Deck()

    win = GameWindow(d)

    win.draw()