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
from six import iteritems
from sqlalchemy.exc import IntegrityError

from brenda_parser.exceptions import ValidationError
from brenda_parser.models import Reference


@pytest.mark.parametrize("attributes", [
    pytest.param({"body": None},
                 marks=pytest.mark.raises(exception=IntegrityError)),
    {"body": "Cunning et al."},
    pytest.param({"body": "Evil Inc.", "pubmed": "fail"},
                 marks=pytest.mark.raises(exception=ValidationError)),
    {"body": "Vitello et al.", "pubmed": "Pubmed:1234567"}
])
def test_create_reference(session, attributes):
    obj = Reference(**attributes)
    session.add(obj)
    session.commit()
    for attr, value in iteritems(attributes):
        assert getattr(obj, attr) == value


@pytest.mark.parametrize("ref_a, ref_b", [
    pytest.param({"body": "Vitello et al.", "pubmed": "Pubmed:1234567"},
                 {"body": "The Others", "pubmed": "Pubmed:1234567"},
                 marks=pytest.mark.raises(exception=IntegrityError)),
    ({"body": "Batman", "pubmed": "Pubmed:1111111"},
     {"body": "Robin", "pubmed": "Pubmed:2222222"})
])
def test_unique_name(session, ref_a, ref_b):
    obj_a = Reference(**ref_a)
    obj_b = Reference(**ref_b)
    session.add_all([obj_a, obj_b])
    session.commit()
