"""
Web Scraper for Game Data (Powers, Items, Characters)
Scrapes HTML tables and downloads images from game wiki
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path
from urllib.parse import urljoin
import time


class GameDataScraper:
    def __init__(self, base_url=""):
        """
        Initialize the scraper
        
        Args:
            base_url: Base URL of the wiki (e.g., "https://example.com")
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create directories for images
        self.image_dirs = {
            'powers': Path('assets/powers'),
            'items': Path('assets/items'),
            'characters_hud': Path('assets/characters'),
            'characters_portrait': Path('assets/characters')
        }
        for dir_path in self.image_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def download_image(self, image_url, save_path):
        """
        Download an image from URL
        
        Args:
            image_url: URL of the image
            save_path: Path where to save the image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Make URL absolute if it's relative
            if not image_url.startswith('http'):
                image_url = urljoin(self.base_url, image_url)
            
            response = self.session.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Save image
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"  ✓ Downloaded: {save_path.name}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to download {image_url}: {e}")
            return False
    
    def extract_image_url(self, img_tag):
        """
        Extract the best quality image URL from img tag
        
        Args:
            img_tag: BeautifulSoup img tag
            
        Returns:
            str: Image URL or None
        """
        if not img_tag:
            return None
        
        # Try srcset first (higher quality)
        srcset = img_tag.get('srcset', '')
        if srcset:
            # Get the highest quality version (last one in srcset)
            parts = srcset.split(',')
            if parts:
                url = parts[-1].strip().split(' ')[0]
                return url
        
        # Fallback to src
        return img_tag.get('src')
    
    def scrape_powers_table(self, url):
        """
        Scrape powers table from URL and format for app
        
        Args:
            url: URL of the powers page
            
        Returns:
            dict: Dictionary with 'powers', 'combos', and 'combo_powers' keys
        """
        print(f"\n=== Scraping Powers from {url} ===")
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the table (adjust selector based on actual HTML)
            table = soup.find('table')
            if not table:
                print("✗ No table found on page")
                return {"powers": {}, "combos": {}, "combo_powers": {}}
            
            powers = {}  # Basic powers
            combos = {}  # Combo recipes
            combo_powers = {}  # Combo result powers
            
            # First pass: collect all powers to create name->id mapping
            name_to_id = {}
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 6:
                    continue
                power_id = cells[1].get_text(strip=True)
                name = cells[2].get_text(strip=True)
                name_to_id[name] = power_id
            
            # Second pass: process powers with correct ID references
            for idx, row in enumerate(rows, 1):
                cells = row.find_all('td')
                if len(cells) < 6:
                    continue
                
                # Extract icon
                icon_img = cells[0].find('img')
                icon_url = self.extract_image_url(icon_img)
                icon_filename = None
                
                if icon_url:
                    icon_filename = f"power_{idx}.png"
                    icon_path = self.image_dirs['powers'] / icon_filename
                    self.download_image(icon_url, icon_path)
                
                # Extract ID
                power_id = cells[1].get_text(strip=True)
                
                # Extract name
                name = cells[2].get_text(strip=True)
                
                # Extract description
                description = cells[3].get_text(strip=True)
                
                # Extract traits (badges)
                traits = []
                trait_badges = cells[4].find_all('span', class_='inline-block')
                for badge in trait_badges:
                    traits.append(badge.get_text(strip=True))
                
                # Extract evolution recipe
                evolution_recipe = cells[5].get_text(strip=True)
                
                # Create power entry
                power_entry = {
                    'name': name,
                    'description': description,
                    'image': icon_filename,
                    'traits': traits
                }
                
                # Check if it has a recipe (is a combo)
                if evolution_recipe and evolution_recipe != '-':
                    # This is a combo power
                    power_entry['is_combo'] = True
                    
                    # Parse recipe - can have multiple recipes separated by /
                    recipes = evolution_recipe.split(' / ')
                    components_list = []
                    
                    for recipe in recipes:
                        # Parse components (e.g., "Bleed + Iron" or "Vampire Lord + Spider Queen + Mosquito King")
                        component_names = [c.strip() for c in recipe.split('+')]
                        
                        # Convert names to IDs
                        component_ids = []
                        for comp_name in component_names:
                            comp_id = name_to_id.get(comp_name)
                            if comp_id:
                                component_ids.append(comp_id)
                            else:
                                print(f"  ⚠ Warning: Component '{comp_name}' not found in mapping for {name}")
                        
                        if component_ids:
                            components_list.append(component_ids)
                    
                    # Store in combo_powers with IDs
                    power_entry['components'] = components_list[0] if components_list else []
                    combo_powers[power_id] = power_entry
                    
                    # Create combo entries with IDs
                    for component_ids in components_list:
                        if len(component_ids) == 2:
                            # Double combo
                            combo_key = f"{component_ids[0]}+{component_ids[1]}"
                            combos[combo_key] = {
                                'result': power_id,
                                'type': 'COMBO'
                            }
                        elif len(component_ids) == 3:
                            # Triple combo
                            combo_key = f"{component_ids[0]}+{component_ids[1]}+{component_ids[2]}"
                            combos[combo_key] = {
                                'result': power_id,
                                'type': 'TRIPLE'
                            }
                    
                    print(f"  [{idx}] {name} (COMBO: {' + '.join(power_entry['components'])})")
                else:
                    # Basic power
                    powers[power_id] = power_entry
                    print(f"  [{idx}] {name} (ID: {power_id})")
            
            result = {
                'powers': powers,
                'combos': combos,
                'combo_powers': combo_powers
            }
            
            print(f"✓ Scraped {len(powers)} basic powers, {len(combo_powers)} combo powers, {len(combos)} recipes")
            return result
            
        except Exception as e:
            print(f"✗ Error scraping powers: {e}")
            import traceback
            traceback.print_exc()
            return {"powers": {}, "combos": {}, "combo_powers": {}}
    
    def scrape_items_table(self, url):
        """
        Scrape items table from URL and format for app
        
        Args:
            url: URL of the items page
            
        Returns:
            dict: Dictionary with 'items', 'combos', 'combo_items', 'recommendations' keys
        """
        print(f"\n=== Scraping Items from {url} ===")
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            table = soup.find('table')
            if not table:
                print("✗ No table found on page")
                return {"items": {}, "combos": {}, "combo_items": {}, "recommendations": {}}
            
            items = {}
            combos = {}
            combo_items = {}
            
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for idx, row in enumerate(rows, 1):
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue
                
                # Extract icon
                icon_img = cells[0].find('img')
                icon_url = self.extract_image_url(icon_img)
                icon_filename = None
                
                if icon_url:
                    icon_filename = f"item_{idx}.png"
                    icon_path = self.image_dirs['items'] / icon_filename
                    self.download_image(icon_url, icon_path)
                
                # Extract name
                name = cells[1].get_text(strip=True)
                
                # Extract description
                description = cells[2].get_text(strip=True)
                
                # Extract traits
                traits = []
                trait_badges = cells[3].find_all('span', class_='inline-block')
                for badge in trait_badges:
                    traits.append(badge.get_text(strip=True))
                
                # Extract type and recipe
                type_cell = cells[4]
                type_badge = type_cell.find('span', class_='inline-block')
                item_type = type_badge.get_text(strip=True) if type_badge else 'Basic'
                
                # Extract recipe components (if evolved)
                recipe_components = []
                recipe_imgs = type_cell.find_all('img')
                for img in recipe_imgs:
                    component_name = img.get('alt', '').strip()
                    if component_name:
                        recipe_components.append(component_name)
                
                # Create item entry
                item_entry = {
                    'name': name,
                    'description': description,
                    'image': icon_filename,
                    'traits': traits
                }
                
                # Use name as key (items use names, not IDs)
                if recipe_components:
                    # This is a combo item
                    item_entry['is_combo'] = True
                    item_entry['components'] = recipe_components
                    combo_items[name] = item_entry
                    
                    # Create combo entry
                    if len(recipe_components) >= 2:
                        combo_key = '+'.join(recipe_components)
                        combos[combo_key] = {
                            'result': name,
                            'type': 'COMBO'
                        }
                    
                    print(f"  [{idx}] {name} (COMBO: {' + '.join(recipe_components)})")
                else:
                    # Basic item
                    items[name] = item_entry
                    print(f"  [{idx}] {name}")
            
            result = {
                'items': items,
                'combos': combos,
                'combo_items': combo_items,
                'recommendations': {}
            }
            
            print(f"✓ Scraped {len(items)} basic items, {len(combo_items)} combo items, {len(combos)} recipes")
            return result
            
        except Exception as e:
            print(f"✗ Error scraping items: {e}")
            return {"items": {}, "combos": {}, "combo_items": {}, "recommendations": {}}
    
    def scrape_characters_table(self, url):
        """
        Scrape characters table from URL
        
        Args:
            url: URL of the characters page
            
        Returns:
            list: List of character dictionaries
        """
        print(f"\n=== Scraping Characters from {url} ===")
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            table = soup.find('table')
            if not table:
                print("✗ No table found on page")
                return []
            
            characters = []
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for idx, row in enumerate(rows, 1):
                cells = row.find_all('td')
                if len(cells) < 7:
                    continue
                
                # Extract HUD image (48x48)
                hud_img = cells[0].find('img')
                hud_url = self.extract_image_url(hud_img)
                hud_filename = None
                
                if hud_url:
                    hud_filename = f"character_{idx}_hud.png"
                    hud_path = self.image_dirs['characters_hud'] / hud_filename
                    self.download_image(hud_url, hud_path)
                
                # Extract Portrait image (100x100)
                portrait_img = cells[1].find('img')
                portrait_url = self.extract_image_url(portrait_img)
                portrait_filename = None
                
                if portrait_url:
                    portrait_filename = f"character_{idx}_portrait.png"
                    portrait_path = self.image_dirs['characters_portrait'] / portrait_filename
                    self.download_image(portrait_url, portrait_path)
                
                # Extract name
                name = cells[2].get_text(strip=True)
                
                # Extract difficulty
                difficulty_badge = cells[3].find('span', class_='inline-block')
                difficulty = difficulty_badge.get_text(strip=True) if difficulty_badge else 'Unknown'
                
                # Extract starting ball (power)
                starting_ball = cells[4].find('span', class_='text-xs')
                starting_power = starting_ball.get_text(strip=True) if starting_ball else None
                
                # Extract quirks
                quirks = []
                quirks_cell = cells[5]
                quirks_list = quirks_cell.find('ul')
                
                if quirks_list:
                    # Has quirks - extract list items
                    quirk_items = quirks_list.find_all('li')
                    quirks = [li.get_text(strip=True) for li in quirk_items]
                else:
                    # Check if it says "None"
                    quirks_text = quirks_cell.get_text(strip=True)
                    if quirks_text.lower() != 'none':
                        quirks = [quirks_text]
                
                # Extract unlock method
                unlock_method = cells[6].get_text(strip=True)
                
                character_data = {
                    'name': name,
                    'difficulty': difficulty,
                    'starting_power': starting_power,
                    'quirks': quirks if quirks else None,
                    'unlock_method': unlock_method,
                    'hud_icon': hud_filename,
                    'portrait': portrait_filename
                }
                
                characters.append(character_data)
                print(f"  [{idx}] {name} ({difficulty}) - {starting_power}")
            
            print(f"✓ Scraped {len(characters)} characters")
            return characters
            
        except Exception as e:
            print(f"✗ Error scraping characters: {e}")
            return []
    
    def save_to_json(self, data, filename):
        """
        Save data to JSON file
        
        Args:
            data: Data to save
            filename: Output filename
        """
        output_path = Path('config') / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved to {output_path}")
    
    def scrape_all(self, powers_url, items_url, characters_url):
        """
        Scrape all three tables and save to JSON
        
        Args:
            powers_url: URL for powers table
            items_url: URL for items table
            characters_url: URL for characters table
        """
        print("\n" + "="*60)
        print("STARTING GAME DATA SCRAPING")
        print("="*60)
        
        # Scrape powers (returns dict with powers, combos, combo_powers)
        powers_data = self.scrape_powers_table(powers_url)
        if powers_data and powers_data.get('powers'):
            self.save_to_json(powers_data, 'powers.json')
            time.sleep(1)  # Be nice to the server
        
        # Scrape items (returns dict with items, combos, combo_items, recommendations)
        items_data = self.scrape_items_table(items_url)
        if items_data and items_data.get('items'):
            self.save_to_json(items_data, 'items.json')
            time.sleep(1)
        
        # Scrape characters (returns list)
        characters = self.scrape_characters_table(characters_url)
        if characters:
            self.save_to_json(characters, 'characters.json')
        
        print("\n" + "="*60)
        print("SCRAPING COMPLETE")
        print("="*60)
        print(f"Powers: {len(powers_data.get('powers', {}))} basic + {len(powers_data.get('combo_powers', {}))} combos")
        print(f"Items: {len(items_data.get('items', {}))} basic + {len(items_data.get('combo_items', {}))} combos")
        print(f"Characters: {len(characters)}")
        print("\nCheck config/ for JSON files")
        print("Check assets/ for images")


def main():
    """
    Main function - configure URLs and run scraper
    """
    BASE_URL = "https://www.ballxpitguide.com"
    
    POWERS_URL = f"{BASE_URL}/balls"
    ITEMS_URL = f"{BASE_URL}/items"
    CHARACTERS_URL = f"{BASE_URL}/characters"
    
    print("\n" + "="*60)
    print("Ball x Pit Guide - Game Data Scraper")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Powers (Balls): {POWERS_URL}")
    print(f"Items: {ITEMS_URL}")
    print(f"Characters: {CHARACTERS_URL}")
    print("\nStarting scrape...\n")
    
    scraper = GameDataScraper(base_url=BASE_URL)
    scraper.scrape_all(POWERS_URL, ITEMS_URL, CHARACTERS_URL)


if __name__ == "__main__":
    main()
