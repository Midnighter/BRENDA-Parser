# Copyright (c) 2018 Moritz E. Beber
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import pytest

from brenda_parser.exceptions import ValidationError
from brenda_parser.models import InformationField


# from sqlalchemy.exc import IntegrityError


@pytest.mark.parametrize(
    "attributes",
    [
        pytest.param(
            {"acronym": ""}, marks=pytest.mark.raises(exception=ValidationError)
        ),
        pytest.param(
            {"acronym": "I"},
            marks=pytest.mark.raises(exception=ValidationError),
        ),
        pytest.param(
            {"acronym": "on"},
            marks=pytest.mark.raises(exception=ValidationError),
        ),
        {"acronym": "RN"},
        {"acronym": "REF"},
        {"acronym": "IC50"},
        pytest.param(
            {"acronym": "too long"},
            marks=pytest.mark.raises(exception=ValidationError),
        ),
        {"acronym": "SM", "name": "Super Man"},
        pytest.param({"acronym": "SM", "name": "an" * 51})
        # marks=pytest.mark.raises(exception=IntegrityError)),
    ],
)
def test_create_information_field(session, attributes):
    obj = InformationField(**attributes)
    session.add(obj)
    session.commit()
    for attr, value in attributes.items():
        assert getattr(obj, attr) == value
