"""
Gaming Overlay - Interfaz moderna usando DearPyGui
Diseño optimizado para overlays gaming con estilo moderno
"""
import dearpygui.dearpygui as dpg
from PIL import Image
import os
from core.power_manager import PowerManager
from core.item_manager import ItemManager
from core.recommendation_engine import RecommendationEngine
from core.state_manager import StateManager


class GamingOverlay:
    def __init__(self):
        # Managers
        self.power_manager = PowerManager()
        self.item_manager = ItemManager()
        self.state_manager = StateManager(num_power_slots=4, num_item_slots=4)
        self.recommendation_engine = RecommendationEngine(self.power_manager)
        
        # State (ahora delegado a state_manager)
        # self.current_slots y self.current_items se acceden via state_manager
        self.selected_character = None
        self.characters_data = []
        
        # UI Referencias
        self.power_slot_tags = []
        self.item_slot_tags = []
        self.power_recommendation_tags = []
        
        # Theme colors - Gaming style
        self.colors = {
            'bg_dark': [15, 15, 20, 255],
            'bg_medium': [25, 25, 35, 255],
            'bg_light': [35, 35, 50, 255],
            'accent': [100, 200, 255, 255],
            'combo_1': [255, 107, 107, 255],
            'combo_2': [78, 205, 196, 255],
            'combo_3': [255, 230, 109, 255],
            'combo_4': [168, 230, 207, 255],
            'combo_5': [255, 139, 148, 255],
            'text': [220, 220, 230, 255],
            'text_dim': [150, 150, 160, 255],
            'border': [60, 60, 80, 255],
            'recommendation': [255, 200, 50, 180]
        }
        
        # Cargar personajes
        self.load_characters()
        
        # Configurar DearPyGui
        self.setup_dpg()
    
    def load_characters(self):
        """Cargar datos de personajes"""
        import json
        characters_path = os.path.join('config', 'characters.json')
        if os.path.exists(characters_path):
            with open(characters_path, 'r', encoding='utf-8') as f:
                self.characters_data = json.load(f)
    
    def setup_dpg(self):
        """Configurar DearPyGui y crear ventana"""
        dpg.create_context()
        
        # Configurar viewport
        dpg.create_viewport(
            title="Game Power Overlay",
            width=600,
            height=700,
            x_pos=50,
            y_pos=50,
            always_on_top=True,
            decorated=True,
            resizable=False
        )
        
        # Crear tema oscuro gaming
        self.create_theme()
        
        # Crear ventana principal
        with dpg.window(
            label="Power Overlay",
            tag="main_window",
            width=600,
            height=700,
            pos=[0, 0],
            no_move=False,
            no_close=True,
            no_collapse=True
        ):
            # Header - Character Selection
            with dpg.group(horizontal=False):
                dpg.add_text("CHARACTER", color=self.colors['accent'])
                
                char_names = [c['name'] for c in self.characters_data] if self.characters_data else ["No characters"]
                dpg.add_combo(
                    items=char_names,
                    tag="character_combo",
                    callback=self.on_character_changed,
                    width=550,
                    default_value=char_names[0] if char_names else ""
                )
                
                dpg.add_spacer(height=10)
            
            # Powers Section
            with dpg.group(horizontal=False):
                dpg.add_text("POWERS", color=self.colors['accent'])
                dpg.add_spacer(height=5)
                
                # Grid 2x2 de power slots
                with dpg.group(horizontal=True):
                    # Columna 1
                    with dpg.group(horizontal=False):
                        self.create_power_slot(0)
                        dpg.add_spacer(height=10)
                        self.create_power_slot(2)
                    
                    dpg.add_spacer(width=10)
                    
                    # Columna 2
                    with dpg.group(horizontal=False):
                        self.create_power_slot(1)
                        dpg.add_spacer(height=10)
                        self.create_power_slot(3)
                
                dpg.add_spacer(height=20)
            
            # Items Section
            with dpg.group(horizontal=False):
                dpg.add_text("ITEMS", color=self.colors['accent'])
                dpg.add_spacer(height=5)
                
                # Grid 2x2 de item slots
                with dpg.group(horizontal=True):
                    # Columna 1
                    with dpg.group(horizontal=False):
                        self.create_item_slot(0)
                        dpg.add_spacer(height=10)
                        self.create_item_slot(2)
                    
                    dpg.add_spacer(width=10)
                    
                    # Columna 2
                    with dpg.group(horizontal=False):
                        self.create_item_slot(1)
                        dpg.add_spacer(height=10)
                        self.create_item_slot(3)
        
        # Cargar primer personaje por defecto
        if self.characters_data:
            self.load_default_character()
    
    def create_theme(self):
        """Crear tema gaming oscuro"""
        with dpg.theme(tag="global_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, self.colors['bg_dark'])
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, self.colors['bg_medium'])
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, self.colors['bg_light'])
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, self.colors['bg_medium'])
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, self.colors['bg_light'])
                dpg.add_theme_color(dpg.mvThemeCol_Text, self.colors['text'])
                dpg.add_theme_color(dpg.mvThemeCol_Border, self.colors['border'])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)
        
        dpg.bind_theme("global_theme")
    
    def create_power_slot(self, slot_index):
        """Crear un slot de poder"""
        slot_tag = f"power_slot_{slot_index}"
        image_tag = f"power_image_{slot_index}"
        button_tag = f"power_button_{slot_index}"
        text_tag = f"power_text_{slot_index}"
        rec_tag = f"power_rec_{slot_index}"
        
        self.power_slot_tags.append({
            'slot': slot_tag,
            'image': image_tag,
            'button': button_tag,
            'text': text_tag,
            'recommendation': rec_tag
        })
        
        # Child window para el slot (permite bordes de color)
        with dpg.child_window(
            tag=slot_tag,
            width=270,
            height=130,
            border=True
        ):
            # Botón para click derecho (menú)
            with dpg.group(horizontal=False):
                dpg.add_button(
                    tag=button_tag,
                    label=f"Slot {slot_index + 1}",
                    width=250,
                    height=110,
                    callback=lambda: self.show_power_menu(slot_index)
                )
                
                # Texto de recomendación
                dpg.add_text(
                    "",
                    tag=rec_tag,
                    color=self.colors['recommendation'],
                    show=False
                )
    
    def create_item_slot(self, slot_index):
        """Crear un slot de item"""
        slot_tag = f"item_slot_{slot_index}"
        button_tag = f"item_button_{slot_index}"
        
        self.item_slot_tags.append({
            'slot': slot_tag,
            'button': button_tag
        })
        
        with dpg.child_window(
            tag=slot_tag,
            width=270,
            height=130,
            border=True
        ):
            dpg.add_button(
                tag=button_tag,
                label=f"Item {slot_index + 1}",
                width=250,
                height=110,
                callback=lambda: self.show_item_menu(slot_index)
            )
    
    def load_default_character(self):
        """Cargar personaje inicial"""
        if not self.characters_data:
            return
        
        first_char = self.characters_data[0]
        self.selected_character = first_char['name']
        
        # Obtener ball base del personaje
        starting_power_name = first_char.get('starting_power')
        if starting_power_name:
            # Buscar el ID del poder por nombre
            for power_id, power_info in self.power_manager.powers_data.items():
                if power_info['name'] == starting_power_name:
                    self.state_manager.set_power(0, power_id)
                    break
        
        self.refresh_ui()
    
    def on_character_changed(self, sender, app_data):
        """Callback cuando cambia el personaje seleccionado"""
        selected_name = app_data
        
        # Buscar personaje
        for char in self.characters_data:
            if char['name'] == selected_name:
                self.selected_character = selected_name
                
                # Limpiar slots
                self.state_manager.clear_all_powers()
                
                # Cargar ball base
                starting_power_name = char.get('starting_power')
                if starting_power_name:
                    for power_id, power_info in self.power_manager.powers_data.items():
                        if power_info['name'] == starting_power_name:
                            self.state_manager.set_power(0, power_id)
                            break
                
                self.refresh_ui()
                break
    
    def show_power_menu(self, slot_index):
        """Mostrar menú contextual de poderes"""
        # Crear ventana de menú
        if dpg.does_item_exist("power_menu_window"):
            dpg.delete_item("power_menu_window")
        
        # Obtener poderes actuales para contexto
        current_slots = self.state_manager.get_all_powers()
        used_powers = set(pid for pid in current_slots if pid is not None)
        
        # Obtener lista ordenada contextualmente
        power_list = self.recommendation_engine.get_sorted_powers_for_menu(
            current_slots, used_powers
        )
        
        # Crear ventana de menú
        with dpg.window(
            label=f"Select Power for Slot {slot_index + 1}",
            tag="power_menu_window",
            modal=True,
            width=400,
            height=500,
            pos=[200, 150]
        ):
            # Opción: Clear
            if self.state_manager.get_power(slot_index) is not None:
                if dpg.add_button(
                    label="❌ Clear Slot",
                    width=380,
                    callback=lambda: self.clear_power_slot(slot_index)
                ):
                    pass
                dpg.add_spacer(height=10)
            
            # Lista de poderes
            with dpg.child_window(width=380, height=400):
                for power in power_list[:20]:  # Limitar a 20 para no saturar
                    pid = power['id']
                    pinfo = power['info']
                    prefix = power['prefix']
                    
                    label = f"{prefix} {pinfo['name']}"
                    
                    # Usar user_data para pasar parámetros sin closure issues
                    dpg.add_button(
                        label=label,
                        width=360,
                        user_data={'slot': slot_index, 'power_id': pid},
                        callback=self.on_power_selected
                    )
            
            # Botón cerrar
            dpg.add_spacer(height=10)
            dpg.add_button(
                label="Cancel",
                width=380,
                callback=lambda: dpg.delete_item("power_menu_window")
            )
    
    def show_item_menu(self, slot_index):
        """Mostrar menú de items (placeholder)"""
        if dpg.does_item_exist("item_menu_window"):
            dpg.delete_item("item_menu_window")
        
        with dpg.window(
            label=f"Select Item for Slot {slot_index + 1}",
            tag="item_menu_window",
            modal=True,
            width=400,
            height=500,
            pos=[200, 150]
        ):
            dpg.add_text("Item selection - Coming soon")
            dpg.add_spacer(height=10)
            dpg.add_button(
                label="Close",
                width=380,
                callback=lambda: dpg.delete_item("item_menu_window")
            )
    
    def on_power_selected(self, sender, app_data, user_data):
        """Callback cuando se selecciona un poder del menú"""
        slot_index = user_data['slot']
        power_id = user_data['power_id']
        self.select_power(slot_index, power_id)
    
    def select_power(self, slot_index, power_id):
        """Seleccionar un poder para un slot"""
        self.state_manager.set_power(slot_index, power_id)
        dpg.delete_item("power_menu_window")
        self.refresh_ui()
    
    def clear_power_slot(self, slot_index):
        """Limpiar un slot de poder"""
        self.state_manager.clear_power(slot_index)
        dpg.delete_item("power_menu_window")
        self.refresh_ui()
    
    def refresh_ui(self):
        """Actualizar toda la interfaz"""
        # Calcular recomendaciones
        current_slots = self.state_manager.get_all_powers()
        result = self.recommendation_engine.calculate_recommendations(current_slots)
        recommendations = result['recommendations']
        color_groups = result['color_groups']
        
        # Actualizar cada slot
        for i in range(4):
            self.update_power_slot(i, recommendations, color_groups)
    
    def update_power_slot(self, slot_index, recommendations, color_groups):
        """Actualizar un slot de poder"""
        tags = self.power_slot_tags[slot_index]
        power_id = self.state_manager.get_power(slot_index)
        
        # Determinar color del borde
        border_color = self.colors['border']
        for group_idx, group in enumerate(color_groups):
            if slot_index in group:
                # Aplicar color de combo
                color_idx = group_idx % len(self.colors)
                combo_keys = [f'combo_{i+1}' for i in range(5)]
                border_color = self.colors[combo_keys[group_idx % 5]]
                break
        
        # Aplicar color de borde al child window
        if dpg.does_item_exist(tags['slot']):
            # DearPyGui no permite cambiar border color dinámicamente
            # Usaremos el button background como indicador
            pass
        
        # Actualizar botón
        if power_id:
            # Tiene un poder seleccionado
            power_info = self.power_manager.get_power_info(power_id)
            if power_info:
                label = f"✓ {power_info['name']}"
                dpg.configure_item(tags['button'], label=label)
        else:
            # Slot vacío - mostrar recomendación si existe
            rec_id = recommendations[slot_index]
            if rec_id:
                rec_info = self.power_manager.get_power_info(rec_id)
                if rec_info:
                    label = f"💡 {rec_info['name']}"
                    dpg.configure_item(tags['button'], label=label)
                    dpg.configure_item(tags['recommendation'], default_value="Recommended", show=True)
                else:
                    dpg.configure_item(tags['button'], label=f"Slot {slot_index + 1}")
                    dpg.configure_item(tags['recommendation'], show=False)
            else:
                dpg.configure_item(tags['button'], label=f"Slot {slot_index + 1}")
                dpg.configure_item(tags['recommendation'], show=False)
    
    def run(self):
        """Ejecutar overlay"""
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        # Main loop
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
        
        dpg.destroy_context()


def create_overlay():
    """Función helper para crear y ejecutar overlay"""
    overlay = GamingOverlay()
    overlay.run()


if __name__ == "__main__":
    create_overlay()
