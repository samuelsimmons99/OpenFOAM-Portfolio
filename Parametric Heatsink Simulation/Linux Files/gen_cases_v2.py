#!/usr/bin/env python3
FAN_D=80e-3;FT=1.5e-3;FH=35e-3;FL=80e-3;BT=5e-3;SP=2e-3;LP=105e-3
CPU_H=4.5e-3;CPU_W=40e-3;CPU_L=40e-3;TIM_T=0.05e-3;TIM_K=4.0
Q_TOT=150.0;RHO=1.177
FAN_C0=73.99;FAN_C1=-1164.25;FAN_C2=-34615.0
NZ_PLENUM=25;NZ_PRE=10;NZ_CPU=20
NY_CPU=5;NY_SPREAD=3;NY_BASE=4;NY_FIN=18;NY_BYPASS=12
NX_FIN=4;NX_CHAN=8;NX_SIDE=4
CPU_X0=(FAN_D-CPU_W)/2.0;CPU_X1=CPU_X0+CPU_W

def chan_w(p): return p["fin_pitch"]-FT
def side_gap(p): return (FAN_D-(p["n_fins"]*FT+(p["n_fins"]-1)*chan_w(p)))/2.0
def cpu_z0(): return LP+(FL-CPU_L)/2.0
def cpu_z1(): return cpu_z0()+CPU_L
def cpu_vol(): return CPU_W*CPU_L*CPU_H
def cpu_heat(): return Q_TOT/cpu_vol()
def is_cpu_x(xs,xe): return xs>=CPU_X0-1e-9 and xe<=CPU_X1+1e-9

def build_x_strips(p):
    cw=chan_w(p);sg=side_gap(p);nf=p["n_fins"]
    raw=[]
    x=0.0
    raw.append((x,x+sg,'side'));x+=sg
    for i in range(nf):
        raw.append((x,x+FT,'fin'));x+=FT
        if i<nf-1: raw.append((x,x+cw,'chan'));x+=cw
    raw.append((x,x+sg,'side'))
    result=[]
    for (xs,xe,st) in raw:
        splits=[xs]
        for cx in [CPU_X0,CPU_X1]:
            if xs+1e-9<cx<xe-1e-9: splits.append(cx)
        splits=sorted(set(splits));splits.append(xe)
        for i in range(len(splits)-1): result.append((splits[i],splits[i+1],st))
    return result

def strip_nx(xs,xe,st):
    w=xe-xs
    if st=='fin': return max(1,round(NX_FIN*w/FT))
    elif st=='chan': return max(1,round(NX_CHAN*w/3.5e-3))
    else: return max(1,round(NX_SIDE*w/4.25e-3))

def gen_bmd(p):
    strips=build_x_strips(p)
    x_coords=[]
    for (xs,xe,_) in strips:
        if not x_coords or abs(x_coords[-1]-xs)>1e-12: x_coords.append(xs)
    x_coords.append(strips[-1][1])
    y_layers=[(-CPU_H,0.0,'cpu_layer',NY_CPU),(0.0,SP,'spreader',NY_SPREAD),
              (SP,SP+BT,'base',NY_BASE),(SP+BT,SP+BT+FH,'finzone',NY_FIN),
              (SP+BT+FH,FAN_D,'bypass',NY_BYPASS)]
    y_coords=[yl[0] for yl in y_layers]+[y_layers[-1][1]]
    CZ0=cpu_z0();CZ1=cpu_z1()
    z_slabs=[(0.0,LP,'inlet_plenum',NZ_PLENUM),(LP,CZ0,'heatsink_pre',NZ_PRE),
             (CZ0,CZ1,'heatsink_cpu',NZ_CPU),(CZ1,LP+FL,'heatsink_post',NZ_PRE),
             (LP+FL,LP+FL+LP,'outlet_plenum',NZ_PLENUM)]
    z_coords=[sl[0] for sl in z_slabs]+[z_slabs[-1][1]]
    vertices=[];grid={}
    for iz,zv in enumerate(z_coords):
        for iy,yv in enumerate(y_coords):
            for ix,xv in enumerate(x_coords):
                grid[(ix,iy,iz)]=len(vertices);vertices.append((xv,yv,zv))
    def v(ix,iy,iz): return grid[(ix,iy,iz)]
    blocks=[];fan1=[];fan2=[];base_bot=[];top_w=[];side_w=[]
    for iz,(zs,ze,z_label,nz) in enumerate(z_slabs):
        in_hs='heatsink' in z_label;in_cpuz=z_label=='heatsink_cpu'
        for iy,(ys,ye,y_label,ny) in enumerate(y_layers):
            in_cpuy=y_label=='cpu_layer'
            for ix,(xs,xe,st) in enumerate(strips):
                nx=strip_nx(xs,xe,st);in_cpux=is_cpu_x(xs,xe)
                if in_cpuy:
                    zone='cpu' if (in_cpuz and in_cpux) else 'fluid'
                elif y_label in ('spreader','base'):
                    zone='heatsink' if in_hs else 'fluid'
                elif y_label=='finzone':
                    zone='heatsink' if (in_hs and st=='fin') else 'fluid'
                else: zone='fluid'
                bv=[v(ix,iy,iz),v(ix+1,iy,iz),v(ix+1,iy+1,iz),v(ix,iy+1,iz),
                    v(ix,iy,iz+1),v(ix+1,iy,iz+1),v(ix+1,iy+1,iz+1),v(ix,iy+1,iz+1)]
                blocks.append({'v':bv,'n':(nx,ny,nz),'zone':zone})
                if iz==0 and zone=='fluid': fan1.append((bv[0],bv[3],bv[2],bv[1]))
                if iz==len(z_slabs)-1 and zone=='fluid': fan2.append((bv[4],bv[5],bv[6],bv[7]))
                if iy==0: base_bot.append((bv[0],bv[1],bv[5],bv[4]))
                if iy==len(y_layers)-1: top_w.append((bv[3],bv[7],bv[6],bv[2]))
                if ix==0: side_w.append((bv[0],bv[4],bv[7],bv[3]))
                if ix==len(strips)-1: side_w.append((bv[1],bv[2],bv[6],bv[5]))
    def fs(faces): return "\n".join(f"        ({' '.join(str(vi) for vi in f)})" for f in faces)
    def pt(name,ptype,faces): return [f"    {name}","    {",f"        type {ptype};","        faces","        (",fs(faces),"        );","    }"]
    L=["FoamFile","{","    version 2.0; format ascii;","    class dictionary; object blockMeshDict;","}","","scale 1;",""]
    L+=["vertices","("]
    for (xv,yv,zv) in vertices: L.append(f"    ({xv:.7e} {yv:.7e} {zv:.7e})")
    L+=[");",""]
    L+=["blocks","("]
    for b in blocks:
        vs=" ".join(str(vi) for vi in b['v']);nx_,ny_,nz_=b['n']
        L.append(f"    hex ({vs}) {b['zone']} ({nx_} {ny_} {nz_}) simpleGrading (1 1 1)")
    L+=[");",""]
    L+=["edges","(","  );",""]
    L+=["boundary","("]
    L+=pt("fan1_half0","patch",fan1);L+=pt("fan2_half0","patch",fan2)
    L+=pt("base_bottom","wall",base_bot);L+=pt("top_wall","wall",top_w);L+=pt("side_walls","wall",side_w)
    L+=[");","","mergePatchPairs","(","  );"]
    return "\n".join(L)

if __name__=="__main__":
    p={"fin_pitch":5e-3,"n_fins":15}
    bmd=gen_bmd(p)
    out="/home/rinkoa/openfoam13/sims/p5_cpu/system/blockMeshDict"
    import os; os.makedirs(os.path.dirname(out),exist_ok=True)
    with open(out,"w") as f: f.write(bmd)
    print(f"Written to {out}")
    print(f"CPU heat source: {cpu_heat():.3e} W/m3")
    print(f"TIM R: {TIM_T/TIM_K:.2e} m2K/W")
