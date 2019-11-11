import numpy
import sys
import os, glob
import pickle
from scipy import constants
import emcee
from emcee.utils import MPIPool

def MCMC_main(spectra_observed, pars):
    """
    Main function to start the MCMC sampling.

    Parameters
    ==========

    spectra_observed : dictionary
        The observed spectra ordered per phase
    parameters : dictionary
        The model parameters, mcmc parameters and system parameters

    """
    ###### Set the initial positions of the walkers
    parameters, parameters_init = \
                mcmc_initial_positions(parameters,
                                      prev_chain=parameters['previous_walkers'],
                                      dir_previous_chain=parameters['dir_previous_chain'])

    ###### Calculate any additional parameters according to the chosen set of parameters

    ###### Check if the priors are in the accepted range
    for walker in parameters['n_walkers']:

        parameters_add = calc_additional_par(parameters, parameters_init[walker,:])

        while ln_prior(parameters_init[walker,:], parameters, parameters_add) == -np.inf:

            parameters_init[walker,:] = mcmc_initial_positions(parameters,
                                          prev_chain=parameters['previous_walkers'],
                                          dir_previous_chain=parametres['dir_previous_chain'],
                                          single_walker=True)
            parameters_add = calc_additional_par(parameters, parameters_init[walker,:])

    ###### Create the pool
    pool = MPIPool()

    if not pool.is_master():
        pool.wait()
        syst.exit(0)

    sampler = emcee.EnsembleSampler(parameters['n_walkers'], len(parameters['model'].keys()), probab, args=(data_spectra, parameters, parameters_add), pool=pool)

    ###### create the output file for the chain
    OutputDir = '../MCMC_output/'+parameters['object_id']+'/results_'+parameters['jet_type']+'/output'

    NewDirNumber  = 0
    NewDirCreated = False

    while NewDirCreated==False:

        if not os.path.exists(OutputDir+'_'+str(NewDirNumber)):

            os.makedirs(OutputDir+'_'+str(NewDirNumber))
            NewDirCreated = True

        else:

            NewDirNumber += 1

    OutputDir = OutputDir+'_'+str(NewDirNumber)

    f = open(OutputDir+'/MCMC_chain_output.dat', 'a')
    f.close()

    ###### Run the mcmc chain
    for result in sampler.sample(parameters_init, iterations=parameters['n_iter'], storechain=False):
        position = result[0]
        f = open(OutputDir+'/MCMC_chain_output.dat', 'a')
        np.savetxt(f, np.array(position))
        f.close()


def run_burn_in(sampler, mc, p0, sourcename, folder, setnr):
def run_mcmc(sampler, pburn, sourcename, folder, mc):
def save_chains(filename, sampler, pos, state):

def ln_likelihood(x, y, ysigma, z, y_model):

def ln_probab(pars, pars_walker, pars_add, spectra):
    """
        Calculates the probability of the model.

    Parameters
    ==========
    pars : dictionary
        All parameters
    pars_walker : np.array
        The model parameters of the walker
    pars_add : dictionary
        The additional parameters for this jet type
    spectra : dictionary
        The observed spectra ordered per phase
    Returns
    =======
    probability : float
        The probability of the model
    """
    pars_add = calc_additional_par(pars, pars_walker)

    lp = ln_prior(parameters_init[walker,:], parameters, parameters_add)

    if np.isfinite(lp):

        probability, intensity = lp + ln_likelihood(Theta, mass_prim, mass_sec, data_spectra)

        return probability

    return -np.inf

def ymodel(data_nus, z, dictkey_arrays, dict_modelfluxes, *par):

def ln_prior(pars, pars_walker, pars_add):
    """
        Flat priors. The probability is set to -infty if one of the conditions
        is not met.

    Parameters
    ==========
    pars : dictionary
        All parameters
    pars_walker : np.array
        The model parameters of the walker
    pars_add : dictionary
        The additional parameters for this jet type
    Returns
    =======
    probability : float
        -np.inf or 0

    """

    probability = 0.0
    jet_height_above_star = pars['binary']['primary_sma_AU'] * ( 1 + pars_add['mass_ratio']) / np.tan(pars['model']['jet_angle'])

    ###### Primary radius and jet velocity
    if not (pars_walker['primary_radius'] < jet_height_above_star
            and pars['model']['primary_radius']['min'] < pars_walker['primary_radius'] < 0.7 * pars_add['roche_radius_primary']
            and pars_walker['v_edge'] < pars_walker['v_centre']
    ):

        probability = -np.inf

    ###### All model parameters are within the correct range
    for param in pars_walker.keys():

        if not pars['model'][param]['min'] < pars_walker[param] < pars['model'][param]['max']:

            probability = -np.inf

    if not probability==-np.inf:

        ###### The jet cavity angle is smaller than the inner jet angle or jet angle
        if 'jet_cavity_angle' in pars_walker.keys():

            if (pars['jet_type']=='stellar_jet_simple'
                or pars['jet_type']=='stellar_jet'
                or pars['jet_type']=='X_wind_strict'
                or pars['jet_type']=='sdisk_wind_strict'
            ):

                if not pars_walker['jet_cavity_angle'] < pars_walker['jet_angle']:

                    probability = -np.inf

            elif (pars['jet_type']=='x_wind'
                  or pars['jet_type']=='sdisk_wind'
            ):

                if not pars_walker['jet_cavity_angle'] < pars_walker['jet_angle_inner']:

                    probability = -np.inf

        ###### The jet inner angle is smaller than the jet outer angle
        if pars['jet_type']=='sdisk_wind' or pars['jet_type']=='x_wind':

                if not pars_walker['jet_angle_inner'] < pars_walker['jet_angle']:

                    probability = -np.inf


        ###### inner radius of the disk is larger than twice the stellar radius and
        ###### outer radius of the disk is smaller than the roche radius of the companion
        if pars['jet_type']=='sdisk_wind' or pars['jet_type']=='sdisk_wind_strict':

            if not (2.*pars_add['secondary_radius'] < pars_add['disk_radius_in'] < pars_add['disk_radius_out'] < pars_add['roche_radius_s']
            ):

                probability = -np.inf

    return probability

def calc_additional_par(pars, pars_walker):
    """
    calculate any parameter in the system from the model parameters, depending
    on the jet type.

    Parameters
    ==========
    pars : dictionary
        All parameters
    pars_walker : np.array
        The model parameters of the walker

    Returns
    =======
    pars_add : dictionary
        The additional parameters that have to be calculated

    """
    pars_add = {}

    incl_id              = pars['model']['inclination']['id']
    primary_sma_AU       = pars['binary']['primary_asini'] / pars_walker[incl_id]
    secondary_mass       = geometry_binary.calc_mass_sec(pars['binary']['mass_prim'],
                                                pars_walker[incl_id],
                                                pars['binary']['mass_function']):
    mass_ratio           = pars['binary']['mass_prim'] / secondary_mass
    roche_radius_primary = geometry_binary.calc_roche_radius(mass_ratio, 'primary')

    pars_add = {'primary_sma_AU': primary_sma_AU,
                      'secondary_mass': secondary_mass,
                      'mass_ratio':mass_ratio,
                      'roche_radius_primary':roche_radius_primary}

    if pars['jet_type']=='sdisk_wind' or pars['jet_type']=='sdisk_wind_strict':
        G                  = constants.gravitational_constant
        M_sun              = 1.98847e30
        AU                 = 1.496e11
        R_sun              =
        v_edge_id          = pars['model']['v_edge']['id']
        v_centre_id        = pars['model']['v_centre']['id']
        jet_angle_id       = pars[]'model']['jet_angle']['id']
        jet_angle_inner_id = pars[]'model']['jet_angle_inner']['id']
        v_M                = pars_walker[v_edge_id] * np.tan(pars_walker[jet_angle])**.5
        v_in               = v_M * np.tan(pars_walker[jet_angle_inner_id])
        secondary_radius   = 1.01*mass_sec**0.724 * R_sun / AU
        roche_radius_s     = geometry_binary.calc_roche_radius(mass_ratio, 'secondary')
        disk_radius_out    = G * secondary_mass * M_sun \
                          * (1000*pars_walker[v_edge_id])**-2 * AU**-1
        disk_radius_in     = G * secondary_mass * M_sun \
                          * (1000*v_in)**-2 * AU**-1
        parameters_extra = {'v_M': v_M,
                            'v_in': v_in,
                            'secondary_radius': secondary_radius,
                            'roche_radius_s': roche_radius_s,
                            'disk_radius_out': disk_radius_out,
                            'disk_radius_in': disk_radius_in
                            }
        pars_add.update(parameters_extra)

    return pars_add


def prior_range_check():

def mcmc_initial_positions(pars, prev_chain=False, dir_previous_chain=None, single_walker=False):
    """
    Set the initial positions for the mcmc sampling

    Parameters
    ==========
    pars : dictionary
        The model parameters
    prev_chain : boolean
        True if there is a previous chain of walkers
    dir_previous_chain : string
        the directory to the previous chain
    single_walker : boolean
        True if we calculate the postion for just one walker

    Returns
    =======
    pars : dictionary
        The model parameters including the parameter id
    pars_init : np.array
        The initial positions of the parameters
    """

    n_par     = len(pars['model'].keys())
    n_walkers = int(pars['n_walkers'])

    if prev_chain==True:

        OutputDirPrevious = '../MCMC_output/'+pars['object_id']+'/results_'+pars['jet_type']+'/'+dir_previous_chain

        ###### Load the parameter id
        parameter_id = {}
        with open(OutputDirPrevious+'/parameter_id.dat','r') as f:
            lines = f.readlines()

        for line in lines:

            split_line         = line.split()
            par                = split_line[0]
            par_id             = int(split_line[1])
            parameters_id[par] = par_id

        ###### Load the previous walkers
        with open(OutputDirPrevious+'/MCMC_chain_'+pars['jet_type']+'.dat', 'r') as chain_file:
            walkers_lines = chain_file.readlines()[-n_walkers:]

        ###### create the chain array and add the parameter id
        walkers_list = [np.array(walker_line.split()) for walker_line in walkers_lines]
        pars_init = np.random.rand(n_walkers,n_par)

        for param in parameters_id.keys():

            pars['model'][param]['id'] = parameters_id[param]

            for walker in n_walkers:

                pars_init[walker,parameters_id[param]] = walkers_list[walker][parameters_id[param]]

    elif single_walker=False:

        pars_init = np.random.rand(n_walkers,n_par)

        for n,param in enumerate(pars['model'].keys()):

            pars_init[:,n] = pars['model'][param]['min'] + \
                                   ( pars['model'][param]['max'] - pars['model'][param]['min'] )\
                                   * pars_init[:,n]
            pars['model'][param]['id'] = n

    else:

        pars_init = np.random.rand(n_par)

        for param in pars['model'].keys():

            n = pars['model'][param]['id']
            pars_init[n] = pars['model'][param]['min'] + \
                                   ( pars['model'][param]['max'] - pars['model'][param]['min'] )\
                                   * pars_init[n]

    return pars, pars_init
