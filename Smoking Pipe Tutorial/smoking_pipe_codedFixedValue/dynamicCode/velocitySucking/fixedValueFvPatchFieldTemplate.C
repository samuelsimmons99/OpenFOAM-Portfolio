/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2019 OpenCFD Ltd.
    Copyright (C) YEAR AUTHOR, AFFILIATION
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

\*---------------------------------------------------------------------------*/

#include "fixedValueFvPatchFieldTemplate.H"
#include "addToRunTimeSelectionTable.H"
#include "fvPatchFieldMapper.H"
#include "volFields.H"
#include "surfaceFields.H"
#include "unitConversion.H"

//{{{ begin codeInclude

//}}} end codeInclude


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * Local Functions * * * * * * * * * * * * * * //

//{{{ begin localCode

//}}} end localCode


// * * * * * * * * * * * * * * * Global Functions  * * * * * * * * * * * * * //

// dynamicCode:
// SHA1 = b21f103fbe5e08a69817135d8a8fef95c91d443c
//
// unique function name that can be checked if the correct library version
// has been loaded
extern "C" void velocitySucking_b21f103fbe5e08a69817135d8a8fef95c91d443c(bool load)
{
    if (load)
    {
        // Code that can be explicitly executed after loading
    }
    else
    {
        // Code that can be explicitly executed before unloading
    }
}

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

makeRemovablePatchTypeField
(
    fvPatchVectorField,
    velocitySuckingFixedValueFvPatchVectorField
);


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

velocitySuckingFixedValueFvPatchVectorField::
velocitySuckingFixedValueFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF
)
:
    fixedValueFvPatchField<vector>(p, iF)
{
    if (false)
    {
        printMessage("Construct velocitySucking : patch/DimensionedField");
    }
}


velocitySuckingFixedValueFvPatchVectorField::
velocitySuckingFixedValueFvPatchVectorField
(
    const velocitySuckingFixedValueFvPatchVectorField& ptf,
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    fixedValueFvPatchField<vector>(ptf, p, iF, mapper)
{
    if (false)
    {
        printMessage("Construct velocitySucking : patch/DimensionedField/mapper");
    }
}


velocitySuckingFixedValueFvPatchVectorField::
velocitySuckingFixedValueFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const dictionary& dict
)
:
    fixedValueFvPatchField<vector>(p, iF, dict)
{
    if (false)
    {
        printMessage("Construct velocitySucking : patch/dictionary");
    }
}


velocitySuckingFixedValueFvPatchVectorField::
velocitySuckingFixedValueFvPatchVectorField
(
    const velocitySuckingFixedValueFvPatchVectorField& ptf
)
:
    fixedValueFvPatchField<vector>(ptf)
{
    if (false)
    {
        printMessage("Copy construct velocitySucking");
    }
}


velocitySuckingFixedValueFvPatchVectorField::
velocitySuckingFixedValueFvPatchVectorField
(
    const velocitySuckingFixedValueFvPatchVectorField& ptf,
    const DimensionedField<vector, volMesh>& iF
)
:
    fixedValueFvPatchField<vector>(ptf, iF)
{
    if (false)
    {
        printMessage("Construct velocitySucking : copy/DimensionedField");
    }
}


// * * * * * * * * * * * * * * * * Destructor  * * * * * * * * * * * * * * * //

velocitySuckingFixedValueFvPatchVectorField::
~velocitySuckingFixedValueFvPatchVectorField()
{
    if (false)
    {
        printMessage("Destroy velocitySucking");
    }
}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void velocitySuckingFixedValueFvPatchVectorField::updateCoeffs()
{
    if (this->updated())
    {
        return;
    }

    if (false)
    {
        printMessage("updateCoeffs velocitySucking");
    }

//{{{ begin code
    #line 38 "//home/rinkoa/OpenFOAM-v2012/sims/smoking_pipe_codedFixedValue/0/U.boundaryField.Outlet"
//  breath volume, 2 liter
		const scalar vL = 0.002;
		// duration of breathing (s)
		const scalar tB = 1.5;
		// start first breathing (s)
		const  scalar breathingStart = 0.1;
		// repeat breathing each x s
		const scalar nextBreath = 5;
		// run time (s) --> simulation time
		const scalar t = this->db().time().value();
		// access to the fvPatch
		const fvPatch& fvP = this->patch();
		// access to surface normals
		const vectorField& n = fvP.nf();
		// calculate velocity during breathing, assume constant flow rate
		scalar dotVBreath = vL / tB; //m3/s

		//single area of each face
		const scalarField& Af = fvP.magSf();
		// outlet area
		const scalar A = gSum(Af);

		//mean velocity at each face is equal to 0
		scalarField U (this->size(), 0);
		// dynamic condition; start manipulating U field
		if (t > breathingStart)
		{
			// start breathing, first time
			if ((t-breathingStart) < tB)
			{
				U = dotVBreath / A;
			}
		// breathing break
			else
			{
				// second breath for ever
				if ((t-breathingStart) > (nextBreath+tB))
				{
					U = dotVBreath / A;
				}
			}
			//otherwise do nothing
		}
		// set mean velocity normal to the faces
		operator==(U * n);
//}}} end code

    this->fixedValueFvPatchField<vector>::updateCoeffs();
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //

