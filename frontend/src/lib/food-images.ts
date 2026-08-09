import type { Food } from "@/api/types";

const FOOD_IMAGE_FALLBACKS: Record<string, string> = {
  "jollof-rice-chicken":
    "https://images.unsplash.com/photo-1664992960082-0ea299a9c53e?auto=format&fit=crop&w=1200&q=80",
  "fried-rice-chicken":
    "https://images.unsplash.com/photo-1772729440931-e8efd3adc748?auto=format&fit=crop&w=1200&q=80",
  "white-rice-with-chicken-stew":
    "https://images.unsplash.com/photo-1579112965143-9139ed2a522a?auto=format&fit=crop&w=1200&q=80",
  "asun-jollof-rice-chicken":
    "https://images.unsplash.com/photo-1664992960082-0ea299a9c53e?auto=format&fit=crop&w=1200&q=80",
  "asun-fried-rice-chicken":
    "https://images.unsplash.com/photo-1772729440931-e8efd3adc748?auto=format&fit=crop&w=1200&q=80",
  "catfish-pepper-soup-with-yam":
    "https://images.unsplash.com/photo-1662041648634-684d7d09ebbf?auto=format&fit=crop&w=1200&q=80",
  "goat-meat-pepper-soup-with-yam":
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80",
  "boiled-yam-egg-sauce":
    "https://images.unsplash.com/photo-1510693206972-df098062cb71?auto=format&fit=crop&w=1200&q=80",
  "fried-yam-egg-sauce":
    "https://images.unsplash.com/photo-1510693206972-df098062cb71?auto=format&fit=crop&w=1200&q=80",
  "chicken-shawarma":
    "https://images.pexels.com/photos/29306505/pexels-photo-29306505.jpeg?cs=srgb&dl=pexels-nano-erdozain-120534369-29306505.jpg&fm=jpg",
  "chicken-shawarma-sausage":
    "https://images.pexels.com/photos/29306505/pexels-photo-29306505.jpeg?cs=srgb&dl=pexels-nano-erdozain-120534369-29306505.jpg&fm=jpg",
  "indomie-veg":
    "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=1200&q=80",
  "indomie-chicken":
    "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=1200&q=80",
  "indomie-chicken-sausage":
    "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=1200&q=80",
  "indomie-chicken-egg":
    "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=1200&q=80",
  "chicken-chips-chicken-thigh-or-drumstick":
    "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1200&q=80",
  "chicken-chips-chicken-lap":
    "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1200&q=80",
  "onion-cake":
    "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1200&q=80",
  "chicken-buns":
    "https://images.unsplash.com/photo-1604908176997-431f694216cc?auto=format&fit=crop&w=1200&q=80",
  "punjabi-samosa":
    "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=1200&q=80",
  "vegetable-spring-rolls":
    "https://images.unsplash.com/photo-1515022376298-7333f33e704b?auto=format&fit=crop&w=1200&q=80",
  "vegetable-samosa":
    "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=1200&q=80",
};

export function resolveFoodImage(food: Food) {
  return food.image_url || FOOD_IMAGE_FALLBACKS[food.slug] || "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1200&q=80";
}
