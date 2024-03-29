import numpy as np
# Author: Elvis do A. Soares
# Github: @elvissoares
# Date: 2020-06-05
# Updated: 2021-05-31

" ==== FIRE: Fast Inertial Relaxation Engine ===== "

" References: "
"- Bitzek, E., Koskinen, P., Gähler, F., Moseler, M., & Gumbsch, P. (2006). Structural relaxation made simple. Physical Review Letters, 97(17), 1–4. https://doi.org/10.1103/PhysRevLett.97.170201"
"- Guénolé, J., Nöhring, W. G., Vaid, A., Houllé, F., Xie, Z., Prakash, A., & Bitzek, E. (2020). Assessment and optimization of the fast inertial relaxation engine (FIRE) for energy minimization in atomistic simulations and its implementation in LAMMPS. Computational Materials Science, 175. https://doi.org/10.1016/j.commatsci.2020.109584"


" Global variables for the FIRE algorithm"
alpha0 = 0.1
Ndelay = 5
Nmax = 10000
finc = 1.1
fdec = 0.5
fa = 0.99
Nnegmax = 2000

def optimize_fire(x0,f,df,params,atol=1e-4,dt = 0.002,logoutput=False):
    error = 10*atol 
    dtmax = 10*dt
    dtmin = 0.02*dt
    alpha = alpha0
    Npos = 0

    x = x0.copy()
    V = np.zeros(x.shape)
    F = -df(x,params)

    for i in range(Nmax):

        P = (F*V).sum() # dissipated power
        
        if (P>0):
            Npos = Npos + 1
            if Npos>Ndelay:
                dt = min(dt*finc,dtmax)
                alpha = alpha*fa
        else:
            Npos = 0
            dt = max(dt*fdec,dtmin)
            alpha = alpha0
            V = np.zeros(x.shape)

        V = V + 0.5*dt*F
        V = (1-alpha)*V + alpha*F*np.linalg.norm(V)/np.linalg.norm(F)
        x = x + dt*V
        F = -df(x,params)
        V = V + 0.5*dt*F

        error = max(abs(F))
        if error < atol: break

        if logoutput: print(f(x,params),error)

    del V, F  
    return [x,f(x,params),i]

def optimize_fire2(x0,f,df,params,atol=1e-4,dt = 0.002,logoutput=False):
    error = 10*atol 
    dtmax = 10*dt
    dtmin = 0.02*dt
    alpha = alpha0
    Npos = 0
    Nneg = 0

    x = x0.copy()
    V = np.zeros(x.shape)
    F = -df(x,params)

    for i in range(Nmax):

        P = (F*V).sum() # dissipated power
        
        if (P>0):
            Npos = Npos + 1
            Nneg = 0
            if Npos>Ndelay:
                dt = min(dt*finc,dtmax)
                alpha = alpha*fa
        else:
            Npos = 0
            Nneg = Nneg + 1
            if Nneg > Nnegmax: break
            if i> Ndelay:
                dt = max(dt*fdec,dtmin)
                alpha = alpha0
            x = x - 0.5*dt*V
            V = np.zeros(x.shape)
            
        V = V + 0.5*dt*F
        V = (1-alpha)*V + alpha*F*np.linalg.norm(V)/np.linalg.norm(F)
        x = x + dt*V
        F = -df(x,params)
        V = V + 0.5*dt*F

        error = max(abs(F))
        if error < atol: break

        if logoutput: print(f(x,params),error)

    del V, F  
    return [x,f(x,params),i]

############################################
if __name__ == "__main__":

    ###############
    print('========= Optimizing the Rosenbrock function =========')
    print('xmim=',np.array([1.0,1.0]))
    print('fmim=',0.0)

    def gradf(x,params):
        [a,b] = params
        return np.array([-2*(a-x[0])-4*b*(x[1]-x[0]*x[0])*x[0],2*b*(x[1]-x[0]*x[0])])

    def f(x,params):
        [a,b] = params
        return (np.power((a-x[0]),2)+b*np.power((x[1]-x[0]*x[0]),2))

    p = [1,100]
    x0 = np.array([3.0,4.0])

    print('Fire version 1')
    [xmin,fmin,Niter] = optimize_fire(x0,f,gradf,p,1e-6)

    print("xmin = ", xmin)
    print("fmin = ", fmin)
    print("Iterations = ",Niter)

    print('Fire version 2')
    [xmin,fmin,Niter] = optimize_fire2(x0,f,gradf,p,1e-6)

    print("xmin = ", xmin)
    print("fmin = ", fmin)
    print("Iterations = ",Niter)

    ########################
    print('========= Optimizing the Eggholder function =========')
    print('xmim=',np.array([512.0,404.0]))
    print('fmim=',-956.6407)

    def gradf(x,params):
        c0 = params
        arg1 = np.sqrt(np.abs(x[1]+0.5*x[0]+c0))
        arg2 = np.sqrt(np.abs(x[0]-(x[1]+c0)))
        return np.array([-x[0]*(-c0+x[0]-x[1])*np.cos(arg2)/(2*arg2**3)-(c0+x[1])*(c0+0.5*x[0]+x[1])*np.cos(arg1)/(4*arg1**3)-np.sin(arg2),x[1]*(-c0+x[0]-x[1])*np.cos(arg2)/(2*arg2**3)-(c0+x[1])*(c0+0.5*x[0]+x[1])*np.cos(arg1)/(2*arg1**3)-np.sin(arg2)])
        
    def f(x,params):
        c0 = params
        return -(x[1]+c0)*np.sin(np.sqrt(np.abs(x[1]+0.5*x[0]+c0)))-x[0]*np.sin(np.sqrt(np.abs(x[0]-(x[1]+c0))))

    p = 47
    x0 = np.array([0.0,0.0])

    print('Fire version 1')
    [xmin,fmin,Niter] = optimize_fire(x0,f,gradf,p,1e-6,0.1)

    print("xmin = ", xmin)
    print("fmin = ", fmin)
    print("Iterations = ",Niter)

    print('Fire version 2')
    [xmin,fmin,Niter] = optimize_fire2(x0,f,gradf,p,1e-6,0.1)

    print("xmin = ", xmin)
    print("fmin = ", fmin)
    print("Iterations = ",Niter)