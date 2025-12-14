models/players/moff_gideon/body
{
	cull	twosided
	{
        	map models/players/moff_gideon/body
        	blendFunc GL_ONE GL_ZERO
        	rgbGen lightingDiffuseEntity
	}	
	{
		map gfx/models/players/moff_gideon/body_a
		rgbGen lightingDiffuse
	}
	{
		map gfx/effects/chr_white_add_mild
		blendFunc GL_SRC_ALPHA GL_ONE
		tcGen environment
	}
	{	
		map gfx/models/players/moff_gideon/body_a
		rgbGen lightingDiffuse
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
	}
	{
		map gfx/models/players/moff_gideon/body_glow
		blendFunc GL_ONE GL_ONE
		glow
		rgbGen identity
	}
}

models/players/moff_gideon/accessories
{
	cull	twosided
	{
        	map models/players/moff_gideon/accessories
        	blendFunc GL_ONE GL_ZERO
        	rgbGen lightingDiffuseEntity
	}
	{
		map gfx/models/players/moff_gideon/accessories_a
		rgbGen lightingDiffuse
	}
	{
		map gfx/effects/chr_white_add_mild
		blendFunc GL_SRC_ALPHA GL_ONE
		tcGen environment
	}
	{	
		map gfx/models/players/moff_gideon/accessories_a
		rgbGen lightingDiffuse
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
	}
}

models/players/moff_gideon/accessoriesb
{
	{
        	map models/players/moff_gideon/accessoriesb
        	blendFunc GL_ONE GL_ZERO
        	rgbGen lightingDiffuseEntity
	}
	{
        	map gfx/models/players/moff_gideon/accessories_lens
        	blendFunc GL_DST_COLOR GL_SRC_COLOR
        	tcGen environment
    	}
    	{
		map models/players/moff_gideon/accessoriesb
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen lightingDiffuse
	}
	{
		map gfx/models/players/moff_gideon/accessories_spec
		blendFunc GL_SRC_ALPHA GL_ONE
		alphaGen lightingSpecular
	}
}

models/players/moff_gideon/holster_gun
{
	cull	twosided
    {
        map models/players/moff_gideon/holster_gun
        rgbGen lightingDiffuse
    }
    {
        map gfx/models/players/moff_gideon/holster_gun_spec
        blendFunc GL_SRC_ALPHA GL_ONE
        detail
        alphaGen lightingSpecular
    }
}

models/players/moff_gideon/jetpack
{
	cull	twosided
	{
        	map models/players/moff_gideon/jetpack
        	blendFunc GL_ONE GL_ZERO
        	rgbGen lightingDiffuseEntity
	}	
	{
		map gfx/models/players/moff_gideon/jetpack_a
		rgbGen lightingDiffuse
	}
	{
		map gfx/effects/chr_white_add_mild
		blendFunc GL_SRC_ALPHA GL_ONE
		tcGen environment
	}
	{	
		map gfx/models/players/moff_gideon/jetpack_a
		rgbGen lightingDiffuse
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
	}
	{
		map gfx/models/players/moff_gideon/jetpack_glow
		blendFunc GL_ONE GL_ONE
		glow
		rgbGen identity
	}
}