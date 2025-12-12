models/players/sith_stalker/cpu
{
	q3map_nolightmap
    {
        map models/players/sith_stalker/cpu
        blendFunc GL_ONE GL_ZERO
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/cpu_spec
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_COLOR
        detail
        alphaGen lightingSpecular
    }
    {
        animMap 16 models/players/sith_stalker/cpu1 models/players/sith_stalker/cpu2 models/players/sith_stalker/cpu3 models/players/sith_stalker/cpu4 
        blendFunc GL_ONE GL_ONE
        detail
    }
}

models/players/sith_stalker/extras
{
	cull	disable
    {
        map models/players/sith_stalker/extras
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/default_reflect
        blendFunc GL_ONE GL_ONE
        rgbGen lightingDiffuse
        tcGen environment
    }
    {
        map models/players/sith_stalker/extras
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
        rgbGen lightingDiffuse
    }
}

models/players/sith_stalker/head
{
    {
        map models/players/sith_stalker/head
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/default_reflect
        blendFunc GL_ONE GL_ONE
        rgbGen lightingDiffuse
        tcGen environment
    }
    {
        map models/players/sith_stalker/head
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
        rgbGen lightingDiffuse
    }
}

models/players/sith_stalker/hips
{
	cull	disable
    {
        map models/players/sith_stalker/hips
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/default_reflect
        blendFunc GL_ONE GL_ONE
        rgbGen lightingDiffuse
        tcGen environment
    }
    {
        map models/players/sith_stalker/hips
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
        rgbGen lightingDiffuse
    }
}
models/players/sith_stalker/torso
{
	cull	disable
    {
        map models/players/sith_stalker/torso
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/default_reflect
        blendFunc GL_ONE GL_ONE
        rgbGen lightingDiffuse
        tcGen environment
    }
    {
        map models/players/sith_stalker/torso
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
        rgbGen lightingDiffuse
    }
}

models/players/sith_stalker/tabs
{
	cull	disable
    {
        map models/players/sith_stalker/tabs
        blendFunc GL_ONE GL_ZERO
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/tabs_spec
        blendFunc GL_SRC_ALPHA GL_ONE
        detail
        alphaGen lightingSpecular
    }
}

models/players/sith_stalker/head_blue
{
    {
        map models/players/sith_stalker/head_blue
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/default_reflect
        blendFunc GL_ONE GL_ONE
        rgbGen lightingDiffuse
        tcGen environment
    }
    {
        map models/players/sith_stalker/head_blue
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
        rgbGen lightingDiffuse
    }
}

models/players/sith_stalker/tabs_blue
{
	cull	disable
    {
        map models/players/sith_stalker/tabs_blue
        blendFunc GL_ONE GL_ZERO
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/tabs_spec
        blendFunc GL_SRC_ALPHA GL_ONE
        detail
        alphaGen lightingSpecular
    }
}

models/players/sith_stalker/head_red
{
    {
        map models/players/sith_stalker/head_red
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/default_reflect
        blendFunc GL_ONE GL_ONE
        rgbGen lightingDiffuse
        tcGen environment
    }
    {
        map models/players/sith_stalker/head_red
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
        rgbGen lightingDiffuse
    }
}

models/players/sith_stalker/tabs_red
{
	cull	disable
    {
        map models/players/sith_stalker/tabs_red
        blendFunc GL_ONE GL_ZERO
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/tabs_spec
        blendFunc GL_SRC_ALPHA GL_ONE
        detail
        alphaGen lightingSpecular
    }
}

models/players/sith_stalker/torso_red
{
    {
        map models/players/sith_stalker/torso_red
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/default_reflect
        blendFunc GL_ONE GL_ONE
        rgbGen lightingDiffuse
        tcGen environment
    }
    {
        map models/players/sith_stalker/torso_red
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
        rgbGen lightingDiffuse
    }
}

models/players/sith_stalker/torso_blue
{
    {
        map models/players/sith_stalker/torso_blue
        rgbGen lightingDiffuse
    }
    {
        map models/players/sith_stalker/default_reflect
        blendFunc GL_ONE GL_ONE
        rgbGen lightingDiffuse
        tcGen environment
    }
    {
        map models/players/sith_stalker/torso_blue
        blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
        rgbGen lightingDiffuse
    }
}