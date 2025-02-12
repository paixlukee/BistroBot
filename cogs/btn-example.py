
        
        async def button_callback(interaction):
            await interaction.response.defer()
            
            

        button = Button(label="←", custom_id="prev_page", style=discord.ButtonStyle.primary)           


        d_btn.callback = lambda interaction: t_button_callback(interaction, "d", b)

        view = View()
        view.add_item(button)
        
        # no args
        button.callback = button_callback
        
        
            if msg:
                await food_msg.delete()
            try:
                await interaction.message.delete()
            except:
                pass